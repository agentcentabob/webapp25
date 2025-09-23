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
    cur.execute("SELECT * FROM userinformation2 WHERE email = ?", (email,))
    u = cur.fetchone()
    con.close()
    return u


def get_user_by_id(userID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM userinformation2 WHERE userID = ?", (userID,))
    u = cur.fetchone()
    con.close()
    return u


def create_user(name, email, password, role):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO userinformation2 (name, email, password, role) VALUES (?, ?, ?, ?)",
        (name, email, password, role),
    )
    con.commit()
    con.close()


def update_user(userID, name=None, email=None, password=None):
    # only update the provided fields
    con = get_connection()
    cur = con.cursor()
    if name:
        cur.execute(
            "UPDATE userinformation2 SET name = ? WHERE userID = ?",
            (name, userID))
    if email:
        cur.execute(
            "UPDATE userinformation2 SET email = ? WHERE userID = ?",
            (email, userID))
    if password:
        cur.execute(
            "UPDATE userinformation2 SET password = ? WHERE userID = ?",
            (password, userID),)
    con.commit()
    con.close()
