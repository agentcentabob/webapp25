from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, session, flash
import os
import database_manager as dbHandler

app = Flask(__name__)
app.secret_key = 'session_key'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/<page>')
def render_page(page):
    if page.endswith('.html'):
        template_path = os.path.join(app.template_folder, page)
        if os.path.exists(template_path):
            return render_template(page)
        else:
            template_path = os.path.join(app.template_folder, "404.html")
            return render_template('404.html'), 404


@app.route('/articles.html', methods=['GET'])
def data():
    data = dbHandler.listExtension()
    return render_template('/articles.html', content=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['psw']

        # Simple example: replace with database check
        if username == 'admin' and password == 'password':
            session['user'] = username
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html', hide_search=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
