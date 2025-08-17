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