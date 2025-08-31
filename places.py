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


def add_place(title, description, username, classes):
    sql = "SELECT id FROM users WHERE username = ?"
    user_id = db.query(sql, [username])[0][0]
    sql = "INSERT INTO places (title, description, user_id) VALUES (?, ?, ?)"
    db.execute(sql, [title, description, user_id])

    place_id = db.last_insert_id()

    sql = "INSERT INTO place_classes (place_id, title, value) VALUES (?, ?, ?)"
    for place_title, place_value in classes:
        db.execute(sql, [place_id, place_title, place_value])


def add_comment(comment, user_id, place_id):
    sql = """INSERT INTO comments (place_id, user_id, comment)
             VALUES (?, ?, ?)"""
    db.execute(sql, [place_id, user_id, comment])


def get_comments(place_id, page, page_size):
    sql = """
        SELECT comments.comment, users.id AS user_id, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.place_id = ?
        ORDER BY comments.id DESC
        LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [place_id, limit, offset])


def get_classes(place_id):
    sql = "SELECT title, value FROM place_classes WHERE place_id = ?"
    return db.query(sql, [place_id])


def get_places(page, page_size):
    sql = """
        SELECT places.id, places.title, users.username
        FROM places
        JOIN users ON places.user_id = users.id
        ORDER BY places.id DESC
        LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])


def place_count():
    sql = "SELECT COUNT(*) AS count FROM places"
    result = db.query(sql)
    return result[0]["count"] if result else 0


def comment_count(place_id):
    sql = "SELECT COUNT(*) AS count FROM comments WHERE place_id = ?"
    return db.query(sql, [place_id])[0]["count"]


def get_images(place_id):
    sql = "SELECT id FROM images WHERE place_id = ?"
    return db.query(sql, [place_id])


def add_image(place_id, image):
    sql = "INSERT INTO images (place_id, image) VALUES (?, ?)"
    db.execute(sql, [place_id, image])


def get_image(image_id):
    sql = "SELECT image FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    return result[0][0] if result else None


def remove_image(image_id, place_id):
    sql = "DELETE FROM images WHERE id = ? AND place_id = ?"
    db.execute(sql, [image_id, place_id])


def get_place(place_id):
    sql = """SELECT places.title,
    places.id,
    places.description,
    users.username
    FROM places, users
    WHERE places.user_id = users.id
    AND places.id = ?"""
    result = db.query(sql, [place_id])
    return result[0] if result else None


def update_place(place_id, title, description, classes):
    sql = "UPDATE places SET title = ?, description = ? WHERE id = ?"
    db.execute(sql, [title, description, place_id])

    sql = "DELETE FROM place_classes WHERE place_id = ?"
    db.execute(sql, [place_id])

    sql = "INSERT INTO place_classes (place_id, title, value) VALUES (?, ?, ?)"
    for place_title, place_value in classes:
        db.execute(sql, [place_id, place_title, place_value])


def remove_place(place_id):
    sql = "DELETE FROM comments WHERE place_id = ?"
    db.execute(sql, [place_id])
    sql = "DELETE FROM images WHERE place_id = ?"
    db.execute(sql, [place_id])
    sql = "DELETE FROM place_classes WHERE place_id = ?"
    db.execute(sql, [place_id])
    sql = "DELETE FROM places WHERE id = ?"
    db.execute(sql, [place_id])


def find_places(query, page, page_size):
    sql = """
        SELECT DISTINCT places.id, places.title
        FROM places
        LEFT JOIN place_classes ON places.id = place_classes.place_id
        WHERE places.title LIKE ?
           OR places.description LIKE ?
           OR place_classes.title LIKE ?
           OR place_classes.value LIKE ?
        ORDER BY places.id DESC
        LIMIT ? OFFSET ?
    """
    like = "%" + query + "%"
    offset = (page - 1) * page_size
    return db.query(sql, [like, like, like, like, page_size, offset])


def count_places(query):
    sql = """
        SELECT COUNT(DISTINCT places.id) AS count
        FROM places
        LEFT JOIN place_classes ON places.id = place_classes.place_id
        WHERE places.title LIKE ?
           OR places.description LIKE ?
           OR place_classes.title LIKE ?
           OR place_classes.value LIKE ?
    """
    like = "%" + query + "%"
    rows = db.query(sql, [like, like, like, like])
    return rows[0]["count"] if rows else 0
