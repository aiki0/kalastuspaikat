from werkzeug.security import generate_password_hash, check_password_hash

import db

def get_user(username):
    sql = "SELECT id, username FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if result:
        user_id, username = result[0]
        return {"id": user_id, "username": username}
    return None

def get_items(username):
    sql = """SELECT items.id, items.title, items.description
             FROM items
             JOIN users ON items.user_id = users.id
             WHERE users.username = ?
             ORDER BY items.id DESC"""
    return db.query(sql, [username])

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])
        if not result:
            return False
        user_id = result[0]["id"]
        password_hash = result[0]["password_hash"]
        if check_password_hash(password_hash, password):
            return user_id
        else:
            return None
