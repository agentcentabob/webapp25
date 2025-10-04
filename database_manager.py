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


# user log in (thanks farley)
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
    cur.execute("SELECT * FROM userinformation2 WHERE userID = ?", (user_ID,))
    u = cur.fetchone()
    con.close()
    return u


def create_user(name, email, password):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO userinformation2 "
        "(user_name, user_email, user_password) "
        "VALUES (?, ?, ?)",
        (name, email, password),
    )
    con.commit()
    con.close()


def update_user(user_ID, user_name=None, user_email=None, user_password=None):
    # only update the provided fields
    con = get_connection()
    cur = con.cursor()
    if user_name:
        cur.execute(
            "UPDATE userinformation2 SET name = ? WHERE userID = ?",
            (user_name, user_ID))
    if user_email:
        cur.execute(
            "UPDATE userinformation2 SET email = ? WHERE userID = ?",
            (user_email, user_ID))
    if user_password:
        cur.execute(
            "UPDATE userinformation2 SET password = ? WHERE userID = ?",
            (user_password, user_ID),)
    con.commit()
    con.close()


# note functions
def get_user_notes(user_id):
    """Get all notes for a user, ordered by most recently updated"""
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM notes WHERE user_id = ? ORDER BY updated_at DESC",
        (user_id,)
    )
    notes = cur.fetchall()
    con.close()
    return notes


def get_note_by_id(note_id):
    """Get a specific note by ID"""
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    note = cur.fetchone()
    con.close()
    return note


def create_note(title, content, user_id):
    """Create a new note"""
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO notes (title, content, user_id) VALUES (?, ?, ?)",
        (title, content, user_id)
    )
    note_id = cur.lastrowid
    con.commit()
    con.close()
    return note_id


def update_note(note_id, title=None, content=None):
    """Update a note's title and/or content"""
    con = get_connection()
    cur = con.cursor()

    if title is not None and content is not None:
        cur.execute((
                "UPDATE notes SET title = ?, content = ?, "
                "updated_at = CURRENT_TIMESTAMP WHERE id = ?"),
            (title, content, note_id)
        )

    elif title is not None:
        cur.execute((
            "UPDATE notes SET title = ?, "
            "updated_at = CURRENT_TIMESTAMP WHERE id = ?"),
            (title, note_id)
        )
    elif content is not None:
        cur.execute((
            "UPDATE notes SET content = ?,"
            "updated_at = CURRENT_TIMESTAMP WHERE id = ?",)
            (content, note_id)
        )

    con.commit()
    con.close()


def delete_note(note_id):
    """Delete a note"""
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    con.commit()
    con.close()


def verify_note_ownership(note_id, user_id):
    """Check if a note belongs to a user"""
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT id FROM notes WHERE id = ? AND user_id = ?",
        (note_id, user_id)
    )
    result = cur.fetchone()
    con.close()
    return result is not None
