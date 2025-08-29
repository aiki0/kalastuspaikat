import db
def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)
    
    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)
    return classes

def add_item(title, description, username, classes):
    sql = "SELECT id FROM users WHERE username = ?"
    user_id = db.query(sql, [username])[0][0]
    sql = "INSERT INTO items (title, description, user_id) VALUES (?, ?, ?)"
    db.execute(sql, [title, description, user_id])

    item_id = db.last_insert_id()
    sql = "INSERT INTO item_classes (item_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])
def get_classes(item_id):
    sql = "SELECT title, value FROM item_classes WHERE item_id = ?"
    return db.query(sql, [item_id])

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
    result = db.query(sql, [item_id])
    return result[0] if result else None

def update_item(item_id, title, description):
    sql = "UPDATE items SET title = ?, description = ? WHERE id = ?"
    db.execute(sql, [title, description, item_id])

def remove_item(item_id):
    sql = "DELETE FROM item_classes WHERE item_id = ?"
    db.execute(sql, [item_id])
    sql = "DELETE FROM items WHERE id = ?"
    db.execute(sql, [item_id])

def find_items(query, rating=None):
    sql = """SELECT items.id, items.title, items.description, users.username
    FROM items, users
    WHERE items.user_id = users.id
    AND (items.title LIKE ? OR items.description LIKE ?)"""
    
    params = ["%" + query + "%", "%" + query + "%"]
    
    if rating is not None:
        sql += " AND items.rating = ?"
        params.append(rating)
    
    sql += " ORDER BY items.id DESC"
    
    return db.query(sql, params)
