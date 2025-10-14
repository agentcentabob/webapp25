from flask import Flask, render_template, request  # , jsonify
from flask import flash, redirect, url_for, session, abort
from datetime import timedelta
# from werkzeug.utils import secure_filename
import os
import binascii
import database_manager as dbh
import markdown2
import uuid
import json

app = Flask(__name__)
app.secret_key = "session_key"
app.permanent_session_lifetime = timedelta(days=30)


def is_logged_in():
    return "user" in session


def get_current_user():
    return session.get("user", None)


# upload images constants
NOTEIMG_UPLOAD_FOLDER = 'static/noteimg_uploads'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

if not os.path.exists(NOTEIMG_UPLOAD_FOLDER):
    os.makedirs(NOTEIMG_UPLOAD_FOLDER)


def allowed_image_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


# home page render
@app.route("/")
def home():
    user = get_current_user()
    return render_template("index.html", user=user)


# articles
@app.route("/articles", methods=["GET"])
def data():
    data = dbh.listExtension()
    user = get_current_user()
    return render_template("/articles.html", content=data, user=user)


@app.route("/article/<int:user_id>/<int:article_id>")
def article(user_id, article_id):
    article_data = dbh.get_article_by_id(
        user_id, article_id)
    if not article_data:
        abort(404)
    article_html = markdown2.markdown(
        article_data[10])
    print("Markdown converted:")
    user = get_current_user()
    return render_template(
        "article_view.html",
        article=article_data,
        article_html=article_html,
        user=user)


# account settings
@app.route("/account")
def account():
    if is_logged_in():
        user = get_current_user()
        return render_template("account_settings.html",
                               user=user, hide_search=True)
    else:
        return redirect(url_for("login"))


# rendering user page
@app.route("/user/<int:user_id>")
def user_profile(user_id):
    user_data = dbh.get_user_by_id(user_id)
    if not user_data:
        abort(404)

    articles = dbh.get_user_articles(user_id)
    user = get_current_user()
    is_own_profile = user and user["id"] == user_id

    return render_template("user_profile.html",
                           profile_user=user_data,
                           articles=articles,
                           is_own_profile=is_own_profile,
                           user=user)


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
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        # check all fields filled
        if not username or not email or not password:
            flash("Please fill in all fields", "error")
            return redirect(url_for("join"))

        # check username/email availability
        if dbh.user_exists(username=username):
            flash("Username unavailable", "error")
            return redirect(url_for("join"))
        if dbh.user_exists(email=email):
            flash("Email already in use", "error")
            return redirect(url_for("join"))

        # create new user
        dbh.create_user(username=username, email=email,
                        password=password)

        # retrieve new user and store in session
        new_user = dbh.get_user_by_email(email)
        session["user"] = {
            "id": new_user[0],
            "name": new_user[1],
            "email": new_user[2],
            "pfp": new_user[4],
        }

        flash("Account created successfully!", "success")
        return redirect(url_for("home"))

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
    new_bio = request.form.get("bio")
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

    # update bio if provided
    if new_bio:
        dbh.update_user_bio(user_id, new_bio)
        updated_fields.append("bio")

    # handle profile picture upload
    if 'pfp' in request.files:
        file = request.files['pfp']
        if file and file.filename != '':
            # save file to uploads folder (must be in static for flask to
            # serve unless new route is created)
            os.makedirs('static/uploads', exist_ok=True)
            filename = f"pfp_{user_id}_{binascii.
                                        hexlify(os.urandom(8)).decode()}.png"
            filepath = os.path.join('static/uploads', filename)
            file.save(filepath)
            # update database with new pfp path
            dbh.update_user(user_ID=user_id, user_pfp=f"/{filepath}")
            updated_fields.append("profile picture")

    # refresh session with updated info
    updated_user = dbh.get_user_by_id(user_id)
    session["user"] = {
        "id": updated_user[0],
        "name": updated_user[1],
        "email": updated_user[2],
        "pfp": updated_user[4],
    }

    if updated_fields:
        details = ", ".join(updated_fields)
        flash(f"Account details updated!\n({details})", "success")
    else:
        flash("No changes made", "info")

    return redirect(url_for("user_profile", user_id=user_id))


# delete account (deferred task)
@app.route("/deleteacc", methods=["POST"])
def deleteacc():
    user = get_current_user()
    if not user:
        flash("You must be logged in to delete your account", "error")
        return redirect(url_for("login"))

    # optional: confirm password before deletion
    password = request.form.get("password", "")
    if user["password"] != password:
        flash("Incorrect password", "error")
        return redirect(url_for("account"))

    # delete the user
    dbh.delete_user(user["id"])
    session.pop("user", None)
    flash("Account deleted successfully", "success")
    return redirect(url_for("home"))


# notes
@app.route('/notes/new', methods=['GET', 'POST'])
def new_note():
    if not is_logged_in():
        flash("Sign in to create notes!", "info")
        return redirect(url_for("login"))

    user = get_current_user()

    if request.method == 'POST':
        title = request.form.get('title', 'Untitled')
        content = request.form.get('content', '')
        address = request.form.get('address', '')

        try:
            note_id = dbh.create_note(title, content, user['id'], address)
            flash("Note created successfully!", "success")
            return redirect(url_for('view_note', note_id=note_id))
        except Exception as e:
            print(f"Error creating note: {e}")
            flash("Error creating note", "error")
            return redirect(url_for('new_note'))

    return render_template('notes.html', note_id=None, note_title='',
                           note_address='', note_content='', user=user)


@app.route('/notes/<int:note_id>', methods=['GET', 'POST'])
def view_note(note_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    user = get_current_user()
    note = dbh.get_note_by_id(note_id)

    if not note:
        abort(404)

    if note[0] != user['id']:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        address = request.form.get('address')

        try:
            dbh.update_note(note_id, title, content, address)
            flash("Note saved!", "success")
            return redirect(url_for('view_note', note_id=note_id))
        except Exception as e:
            print(f"Error saving note: {e}")
            flash("Error saving note", "error")

    return render_template('notes.html',
                           note_id=note[1],
                           note_title=note[2],
                           note_address=note[3],
                           note_content=note[6],
                           user=user)


@app.route('/notes/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    user = get_current_user()

    # verify ownership
    if not dbh.verify_note_ownership(note_id, user['id']):
        abort(403)

    try:
        dbh.delete_note(note_id)
        flash("Note deleted successfully!", "success")
        return redirect(url_for('notes_library'))
    except Exception as e:
        print(f"Error deleting note: {e}")
        flash("Error deleting note", "error")
        return redirect(url_for('view_note', note_id=note_id))


@app.route('/notes/<int:note_id>/rename', methods=['POST'])
def rename_note(note_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    user = get_current_user()

    # verify ownership
    if not dbh.verify_note_ownership(note_id, user['id']):
        abort(403)

    try:
        new_title = request.form.get('title')
        dbh.update_note(note_id, new_title)
        flash('Note renamed successfully!', 'success')
        return redirect(url_for('notes_library'))
    except Exception as e:
        print(f"Error renaming note: {e}")
        flash('Failed to rename note', 'error')
        return redirect(url_for('notes_library'))


# upload images
@app.route('/upload-image', methods=['POST'])
def upload_image():
    if not is_logged_in():
        return json.dumps({'error': 'not logged in'}), 401

    if 'file' not in request.files:
        return json.dumps({'error': 'no file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return json.dumps({'error': 'no file selected'}), 400

    if not allowed_image_file(file.filename):
        return json.dumps(
            {'error': 'file type not allowed. use png, jpg, gif, or webp'}
        ), 400

    try:
        # generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{file_ext}"
        filepath = os.path.join(NOTEIMG_UPLOAD_FOLDER, filename)

        file.save(filepath)

        return json.dumps({
            'success': True,
            'url': f'/static/noteimg_uploads/{filename}'
        })
    except Exception as e:
        print(f"image upload error: {e}")
        return json.dumps({'error': 'upload failed'}), 500


# library
@app.route('/notes')
def notes_library():
    if not is_logged_in():
        flash("Sign in to view your notes!", "info")
        return redirect(url_for("login"))

    user = get_current_user()
    print(f"User ID: {user['id']}")  # debugging in terminal
    notes = dbh.get_user_notes(user['id'])
    print(f"Notes found: {len(notes)}")  # debugging in terminal
    print(f"Notes: {notes}")  # debugging in terminal

    return render_template('library.html', notes=notes, user=user)


# rendering other pages
@app.route("/<page>")
def render_page(page):
    # reserved routes
    reserved = ['notes', 'articles', 'login', 'join', 'account',
                'logout', 'update', 'deleteacc']
    if page in reserved:
        return render_template("404.html"), 404

    page += '.html'
    # security? prevent directory traversal attacks
    if ".." in page or page.startswith("/"):
        return render_template("404.html"), 404
    # check if template exists
    template_path = os.path.join(app.template_folder, page)
    if os.path.exists(template_path):
        user = get_current_user()
        return render_template(page, user=user)
    else:
        return render_template("404.html"), 404


# map (includes deferred pin features)
@app.route('/map')
def map_page():
    user = get_current_user()
    return render_template('map.html', user=user)


# search
@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    user = get_current_user()
    if not query:
        return render_template('search.html', query='',
                               results=None, user=user)

    results = dbh.search_all(query)
    total_results = sum(len(results[key]) for key in results)

    return render_template('search.html',
                           query=query,
                           results=results,
                           total_results=total_results,
                           user=user)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
