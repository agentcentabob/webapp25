from flask import Flask, render_template, request
from flask import flash, redirect, url_for, session
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
    template_path = os.path.join(app.template_folder, page)
    if os.path.exists(template_path):
        user = get_current_user()
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
        remember = request.form.get("remember")  # Get checkbox value

        if not email or not password:
            flash("Please fill in all fields", "error")
            return redirect(url_for("login"))

        user = dbh.get_user_by_email(email)

        if user and user[3] == password:
            session["user"] = {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "role": user[4],
            }

            # Set session to permanent if remember me is checked
            if remember:
                session.permanent = True

            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for("login"))

    return render_template("login.html", hide_search=True)


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
