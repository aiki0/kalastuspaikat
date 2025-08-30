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

def add_comment(comment, user_id, item_id):
    sql = """INSERT INTO comments (item_id, user_id, comment)
             VALUES (?, ?, ?)"""
    db.execute(sql, [item_id, user_id, comment])

def get_comments(item_id, page, page_size):
    sql = """
        SELECT comments.comment, users.id AS user_id, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.item_id = ?
        ORDER BY comments.id DESC
        LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [item_id, limit, offset])
    
def get_classes(item_id):
    sql = "SELECT title, value FROM item_classes WHERE item_id = ?"
    return db.query(sql, [item_id])

def get_items(page, page_size):
    sql = """SELECT id, title
             FROM items
             ORDER BY id DESC
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])

def item_count():
    sql = "SELECT COUNT(*) AS count FROM items"
    result = db.query(sql)
    return result[0]["count"] if result else 0

def comment_count(item_id):
    sql = "SELECT COUNT(*) AS count FROM comments WHERE item_id = ?"
    return db.query(sql, [item_id])[0]["count"]

def get_images(item_id):
    sql = "SELECT id FROM images WHERE item_id = ?"
    return db.query(sql, [item_id])

def add_image(item_id, image):
    sql = "INSERT INTO images (item_id, image) VALUES (?, ?)"
    db.execute(sql, [item_id, image])


def get_image(image_id):
    sql = "SELECT image FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    return result[0][0] if result else None

def remove_image(image_id, item_id):
    sql = "DELETE FROM images WHERE id = ? AND item_id = ?"
    db.execute(sql, [image_id, item_id])

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

def update_item(item_id, title, description, classes):
    sql = "UPDATE items SET title = ?, description = ? WHERE id = ?"
    db.execute(sql, [title, description, item_id])
    
    sql = "DELETE FROM item_classes WHERE item_id = ?"
    db.execute(sql, [item_id])

    sql = "INSERT INTO item_classes (item_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])

def remove_item(item_id):
    sql = "DELETE FROM comments WHERE item_id = ?"
    db.execute(sql, [item_id])
    sql = "DELETE FROM images WHERE item_id = ?"
    db.execute(sql, [item_id])
    sql = "DELETE FROM item_classes WHERE item_id = ?"
    db.execute(sql, [item_id])
    sql = "DELETE FROM items WHERE id = ?"
    db.execute(sql, [item_id])

def find_items(query):
    sql = """
        SELECT DISTINCT items.id, items.title
        FROM items
        LEFT JOIN item_classes ON items.id = item_classes.item_id
        WHERE items.title LIKE ?
           OR items.description LIKE ?
           OR item_classes.title LIKE ?
           OR item_classes.value LIKE ?
        ORDER BY items.id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like, like, like])
