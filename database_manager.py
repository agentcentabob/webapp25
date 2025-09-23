import sqlite3 as sql
# import random
# import string
# from datetime import datetime

DB_PATH = "database/data_source.db"

# articles page


def listExtension():
    con = sql.connect("database/data_source.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM notes").fetchall()
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
