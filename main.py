from flask import Flask, render_template, request, jsonify
from flask import flash, redirect, url_for, session, abort
from datetime import timedelta
import os
import database_manager as dbh

app = Flask(__name__)
app.secret_key = "session_key"
app.permanent_session_lifetime = timedelta(days=30)


def is_logged_in():
    return "user" in session


def get_current_user():
    return session.get("user", None)


# rendering pages
@app.route("/")
def home():
    user = get_current_user()
    return render_template("index.html", user=user)


@app.route("/<page>")
def render_page(page):
    page += '.html'
    # security? prevent directory traversal attacks
    if ".." in page or page.startswith("/"):
        return render_template("404.html"), 404
    # check if template exists
    template_path = os.path.join(app.template_folder, page)
    if os.path.exists(template_path):
        user = get_current_user()
        # pass the page name to the template render not the full path
        return render_template(page, user=user)
    else:
        return render_template("404.html"), 404


@app.route("/articles", methods=["GET"])
def data():
    data = dbh.listExtension()
    user = get_current_user()
    return render_template("/articles.html", content=data, user=user)


# account settings
@app.route("/account")
def account():
    if is_logged_in():
        user = get_current_user()
        return render_template("account_settings.html",
                               user=user, hide_Search=True)
    else:
        return redirect(url_for("login"))


# log in page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember")  # checkbox value

        if not email or not password:
            flash("Please fill in all fields", "error")
            return redirect(url_for("login"))

        usere = dbh.get_user_by_email(email)

        if usere and usere[3] == password:
            session["user"] = {
                "id": usere[0],
                "name": usere[1],
                "email": usere[2],
                "pfp": usere[4],
            }

            if remember:
                session.permanent = True

            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for("login"))

    return render_template("login.html", hide_search=True)


# create account page
@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember")  # checkbox value

        if not email or not password:
            flash("Please fill in all fields", "error")
            return redirect(url_for("login"))

        usere = dbh.get_user_by_email(email)

        if usere and usere[3] == password:
            session["user"] = {
                "id": usere[0],
                "name": usere[1],
                "email": usere[2],
                "pfp": usere[4],
            }

            if remember:
                session.permanent = True

            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for("login"))

    return render_template("create_account.html", hide_search=True)


# account settings page
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    flash("Logout successful!", "success")
    return redirect(url_for("home"))


@app.route("/update", methods=["POST"])
def update():
    user = get_current_user()
    user_id = user["id"]
    new_username = request.form.get("username")
    new_email = request.form.get("email")
    new_password = request.form.get("password")
    updated_fields = []

    # check for duplicate username
    if new_username:
        if dbh.user_exists(username=new_username, exclude_id=user_id):
            flash("Username unavailable", "error")
            return redirect(url_for("account"))
        dbh.update_user(user_ID=user_id, user_name=new_username)
        updated_fields.append("username")

    # check for duplicate email
    if new_email:
        if dbh.user_exists(email=new_email, exclude_id=user_id):
            flash("Email already in use", "error")
            return redirect(url_for("account"))
        dbh.update_user(user_ID=user_id, user_email=new_email)
        updated_fields.append("email")

    # update password if provided
    if new_password:
        dbh.update_user(user_ID=user_id, user_password=new_password)
        updated_fields.append("password")

    # refresh session with updated info
    updated_user = dbh.get_user_by_id(user_id)
    session["user"] = {
        "id": updated_user[0],
        "name": updated_user[1],
        "email": updated_user[2],
        "role": updated_user[4],
    }

    if updated_fields:
        details = ", ".join(updated_fields)
        flash(f"Account details updated!\n({details})", "success")
    else:
        flash("No changes made", "info")

    return redirect(url_for("account"))


# notes
@app.route('/notes')
def notes_list():
    if not is_logged_in():
        return redirect(url_for("login"))

    user = get_current_user()
    notes = dbh.get_user_notes(user['id'])
    return render_template('notes_list.html', notes=notes, user=user)


@app.route('/notes/new')
def new_note():
    if not is_logged_in():
        return redirect(url_for("login"))

    user = get_current_user()
    return render_template('notes.html', note_id=None, note_title='',
                           note_content='', user=user)


@app.route('/notes/<int:note_id>')
def view_note(note_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    user = get_current_user()
    note = dbh.get_note_by_id(note_id)

    if not note:
        abort(404)

    if note[0] != user['id']:  # note[0] is user_id
        abort(403)

    return render_template('blank.html',
                           note_id=note[1],
                           note_title=note[2],
                           note_content=note[6],
                           user=user)


@app.route('/api/notes', methods=['POST'])
def create_note():
    if not is_logged_in():
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    user = get_current_user()
    data = request.json
    title = data.get('title', 'Untitled')
    content = data.get('content', '')

    note_id = dbh.create_note(title, content, user['id'])
    return jsonify({'success': True, 'note_id': note_id})


@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    if not is_logged_in():
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    user = get_current_user()

    # Verify ownership
    if not dbh.verify_note_ownership(note_id, user['id']):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    data = request.json
    title = data.get('title')
    content = data.get('content')

    dbh.update_note(note_id, title, content)
    return jsonify({'success': True})


@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    if not is_logged_in():
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    user = get_current_user()

    # Verify ownership
    if not dbh.verify_note_ownership(note_id, user['id']):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    dbh.delete_note(note_id)
    return jsonify({'success': True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
