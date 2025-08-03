import db

def add_item(title, description, username):
    sql = "SELECT id FROM users WHERE username = ?"
    user_id = db.query(sql, [username])[0][0]
    sql = "INSERT INTO items (title, description, user_id) VALUES (?, ?, ?)"
    db.execute(sql, [title, description, user_id])

def get_items():
    sql = "SELECT id, title from items order by id desc"
    return db.query(sql)

def get_item(item_id):
    sql = """SELECT items.title,
    items.id,
    items.description,
    users.username
    FROM items, users
    WHERE items.user_id = users.id
    AND items.id = ?"""
    return db.query(sql, [item_id])[0]

def update_item(item_id, title, description):
    sql = "UPDATE items SET title = ?, description = ? WHERE id = ?"
    db.execute(sql, [title, description, item_id])
def remove_item(item_id):
    sql = "DELETE FROM items WHERE id = ?"
    db.execute(sql, [item_id])

def find_items(query, rating=None):
    sql = """SELECT items.id, items.title, items.description, users.username
    FROM items, users
    WHERE items.user_id = users.id
    AND (items.title LIKE ? OR items.description LIKE ?)"""
    
    params = ['%' + query + '%', '%' + query + '%']
    
    if rating is not None:
        sql += " AND items.rating = ?"
        params.append(rating)
    
    sql += " ORDER BY items.id DESC"
    
    return db.query(sql, params)