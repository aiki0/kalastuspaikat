import random

import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM places")
db.execute("DELETE FROM comments")

user_count = 1000
place_count = 10**6
comment_count = 10**7

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username) VALUES (?)",
               ["user" + str(i)], )

for i in range(1, place_count + 1):
    user_id = random.randint(1, user_count)
    db.execute(
        """INSERT INTO places (title, description, user_id)
           VALUES (?, ?, ?)""",
        [f"place{i}", f"description{i}", user_id])


for i in range(1, comment_count + 1):
    user_id = random.randint(1, user_count)
    place_id = random.randint(1, place_count)
    db.execute(
        """INSERT INTO comments (place_id, user_id, comment)
           VALUES (?, ?, ?)""",
        [place_id, user_id, f"comment{i}"])


db.commit()
db.close()
