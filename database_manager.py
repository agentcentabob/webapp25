import sqlite3 as sql

DB_PATH = "database/data_source.db"


# articles page
# modified to include reference to users from user table via primary key
def listExtension():
    con = sql.connect("database/data_source.db")
    cur = con.cursor()
    data = cur.execute(
        "SELECT a.*, u.user_name FROM articles a "
        "JOIN userinformation2 u ON a.user_ID = u.user_ID "
        "ORDER BY a.date_modified DESC"
    ).fetchall()
    con.close()
    return data


# user functions
def get_connection():
    con = sql.connect(DB_PATH)
    # Enable foreign keys
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def get_user_by_email(email):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM userinformation2 "
        "WHERE user_email = ?",
        (email,)
    )
    u = cur.fetchone()
    con.close()
    return u


def get_user_by_id(user_ID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM userinformation2 WHERE user_ID = ?", (user_ID,))
    u = cur.fetchone()
    con.close()
    return u


def create_user(username, email, password):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO userinformation2 "
        "(user_name, user_email, user_password) "
        "VALUES (?, ?, ?)",
        (username, email, password),
    )
    con.commit()
    con.close()


def update_user(user_ID, user_name=None, user_email=None,
                user_password=None, user_pfp=None):
    # only update the provided fields
    con = get_connection()
    cur = con.cursor()
    if user_name:
        cur.execute(
            "UPDATE userinformation2 SET user_name = ? WHERE user_id = ?",
            (user_name, user_ID))
    if user_email:
        cur.execute(
            "UPDATE userinformation2 SET user_email = ? WHERE user_id = ?",
            (user_email, user_ID))
    if user_password:
        cur.execute(
            "UPDATE userinformation2 SET user_password = ? WHERE user_id = ?",
            (user_password, user_ID),)
    if user_pfp:
        cur.execute(
            "UPDATE userinformation2 SET user_pfp = ? WHERE user_id = ?",
            (user_pfp, user_ID))
    con.commit()
    con.close()


def user_exists(username=None, email=None, exclude_id=None):
    con = get_connection()
    cur = con.cursor()
    if username:
        cur.execute(
            "SELECT 1 FROM userinformation2 WHERE "
            "LOWER(user_name) = LOWER(?) AND user_ID != ?",
            (username, exclude_id),
        )
        if cur.fetchone():
            con.close()
            return True
    if email:
        cur.execute(
            "SELECT 1 FROM userinformation2 WHERE "
            "LOWER(user_email) = LOWER(?) AND user_id != ?",
            (email, exclude_id),
        )
        if cur.fetchone():
            con.close()
            return True
    con.close()
    return False


# search functions
def get_all_users():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM userinformation2")
    users = cur.fetchall()
    con.close()
    return users


def get_all_notes():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT n.user_id, n.note_ID, n.note_title, n.address,
               n.date_modified, n.date_created, n.note_md
        FROM notes n
        ORDER BY n.date_modified DESC
    """)
    notes = cur.fetchall()
    con.close()
    return notes


# note functions
def get_user_notes(user_ID):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM notes WHERE user_ID = ? ORDER BY date_modified DESC",
        (user_ID,)
    )
    notes = cur.fetchall()
    con.close()
    return notes


def get_note_by_id(note_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM notes WHERE note_ID = ?", (note_id,))
    note = cur.fetchone()
    con.close()
    return note


def create_note(title, content, user_id, address=None):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO notes (note_title, address, note_md,"
        " user_id, date_modified) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
        (title, address, content, user_id)
    )
    note_id = cur.lastrowid
    con.commit()
    con.close()
    return note_id


def update_note(note_id, title=None, content=None, address=None):
    con = get_connection()
    cur = con.cursor()

    updates = []
    params = []

    if title is not None:
        updates.append("note_title = ?")
        params.append(title)
    if address is not None:
        updates.append("address = ?")
        params.append(address)
    if content is not None:
        updates.append("note_md = ?")
        params.append(content)

    if updates:
        updates.append("date_modified = CURRENT_TIMESTAMP")
        params.append(note_id)
        query = f"UPDATE notes SET {', '.join(updates)} WHERE note_ID = ?"
        cur.execute(query, params)

    con.commit()
    con.close()


def delete_note(note_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM notes WHERE note_ID = ?", (note_id,))
    con.commit()
    con.close()


def verify_note_ownership(note_id, user_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT note_ID FROM notes WHERE note_ID = ? AND user_id = ?",
        (note_id, user_id)
    )
    result = cur.fetchone()
    con.close()
    return result is not None


def get_article_by_id(user_id, article_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT a.*, u.user_name FROM articles a "
        "JOIN userinformation2 u ON a.user_ID = u.user_ID "
        "WHERE a.user_ID = ? AND a.article_ID = ?",
        (user_id, article_id)
    )
    article = cur.fetchone()
    con.close()
    return article


# profile
def get_user_articles(user_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM articles WHERE user_ID = ? ORDER BY date_modified DESC",
        (user_id,)
    )
    articles = cur.fetchall()
    con.close()
    return articles


def update_last_signin(user_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "UPDATE userinformation2 SET last_signin = "
        "CURRENT_TIMESTAMP WHERE user_ID = ?",
        (user_id,)
    )
    con.commit()
    con.close()


def update_user_bio(user_id, bio):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "UPDATE userinformation2 SET user_bio = ? WHERE user_ID = ?",
        (bio, user_id)
    )
    con.commit()
    con.close()


def update_user_pfp(user_id, pfp_path):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "UPDATE userinformation2 SET user_pfp = ? WHERE user_ID = ?",
        (pfp_path, user_id)
    )
    con.commit()
    con.close()


def search_all(query):
    # centralised search function
    con = get_connection()
    cur = con.cursor()

    results = {
        'users': [],
        'notes': [],
        'articles': []
    }

    # searching users
    # searching users
    cur.execute("SELECT user_id, user_name, user_pfp "
                "FROM userinformation2 WHERE LOWER(user_name) LIKE ?",
                ('%' + query.lower() + '%',))
    users = cur.fetchall()
    for user in users:
        results['users'].append({
            'id': user[0],
            'name': user[1],
            'pfp': user[2],
            'type': 'user'})

    # searching notes
    cur.execute("""SELECT user_id, note_ID, note_title, address, note_md
                FROM notes
                WHERE LOWER(note_title) LIKE ? OR LOWER(note_md) LIKE ?
                OR LOWER(address) LIKE ?
                """, ('%' + query.lower() + '%', '%' + query.lower() + '%',
                '%' + query.lower() + '%'))
    notes = cur.fetchall()
    for note in notes:
        results['notes'].append({
            'id': note[1],
            'title': note[2],
            'content': note[4][:200] + '...'
            if note[4] and len(note[4]) > 200 else note[4],
            'address': note[3],
            'author_id': note[0],
            'type': 'note'
        })

    # searching articles
    cur.execute("""SELECT a.user_id, a.article_id, a.article_title, a.address,
                a.article_md, u.user_name
                FROM articles a
                JOIN userinformation2 u ON a.user_id = u.user_id
                WHERE LOWER(a.article_title) LIKE ? OR
                LOWER(a.article_md) LIKE ?
                """, ('%' + query.lower() + '%', '%' + query.lower() + '%'))

    articles = cur.fetchall()

    for article in articles:
        content = article[4] or ""  # ensure it's a string
        if len(content) > 200:
            snippet = content[:200] + '...'
        else:
            snippet = content
        results['articles'].append({
            'id': article[1],
            'title': article[2],
            'content': snippet,
            'address': article[3],
            'author_id': article[0],
            'author_name': article[5],
            'type': 'article'
        })

    con.close()
    return results


# home page featured articles search (hard coded id 1 from users 1-5)
def get_featured_articles():
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT a.*, u.user_name FROM articles a "
        "JOIN userinformation2 u ON a.user_ID = u.user_ID "
        "WHERE a.article_ID = 1 AND a.user_ID IN (1, 2, 3, 4, 5) "
        "ORDER BY a.user_ID ASC "
        "LIMIT 5"
    )
    articles = cur.fetchall()
    con.close()
    return articles
