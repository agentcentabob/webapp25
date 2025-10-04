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


@app.route("/account")
def account():
    if is_logged_in():
        user = get_current_user()
        return render_template("account_settings.html", user=user)
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember")  # checkbox value

        if not email or not password:
            flash("Please fill in all fields", "error")
            return redirect(url_for("login"))

        user = dbh.get_user_by_email(email)

        if user and user[3] == password:
            session["user"] = {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "pfp": user[4],
            }

            if remember:
                session.permanent = True

            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for("login"))

    return render_template("login.html", hide_search=True)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for("home"))


# notes functions
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

    # Check ownership (note structure: id, title, content,
    # user_id, created_at, updated_at)
    if note[3] != user['id']:  # note[3] is user_id
        abort(403)

    return render_template(
        'notes.html',
        note_id=note[0],       # id
        note_title=note[1],    # title
        note_content=note[2],  # content
        user=user
        )


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
