from werkzeug.security import generate_password_hash, check_password_hash

import db

def get_user(username):
    sql = "SELECT id, username FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if result:
        user_id, username = result[0]
        return {"id": user_id, "username": username}
    return None

def get_places(username, page=1, page_size=10):
    offset = (page - 1) * page_size
    sql = """
        SELECT places.*
        FROM places
        JOIN users ON places.user_id = users.id
        WHERE users.username = ?
        ORDER BY places.id DESC
        LIMIT ? OFFSET ?"""
    return db.query(sql, [username, page_size, offset])

def comment_count(username):
    sql = """
        SELECT COUNT(c.id) AS count
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE u.username = ?"""
    result = db.query(sql, [username])
    return result[0]["count"] if result else 0

def place_count(username):
    sql = """
        SELECT COUNT(*) AS count
        FROM places
        JOIN users ON places.user_id = users.id
        WHERE users.username = ?
    """
    result = db.query(sql, [username])
    return result[0]["count"] if result else 0


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
        

