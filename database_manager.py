import sqlite3 as sql
# import random
# import string
# from datetime import datetime

DB_PATH = "database/data_source.db"


# articles page
def listExtension():
    con = sql.connect("database/data_source.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM articles").fetchall()
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


def update_user(user_ID, user_name=None, user_email=None, user_password=None):
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
