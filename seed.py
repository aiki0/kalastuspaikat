import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM items")
db.execute("DELETE FROM comments")

user_count = 1000
item_count = 10**6
comment_count = 10**7

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username) VALUES (?)",
               ["user" + str(i)], )

for i in range(1, item_count + 1):
    user_id = random.randint(1, user_count)
    db.execute(
        """INSERT INTO items (title, description, user_id) 
           VALUES (?, ?, ?)""",
        [f"item{i}", f"description{i}", user_id])


for i in range(1, comment_count + 1):
    user_id = random.randint(1, user_count)
    item_id = random.randint(1, item_count)
    db.execute(
        """INSERT INTO comments (item_id, user_id, comment)
           VALUES (?, ?, ?)""",
        [item_id, user_id, f"comment{i}"])


db.commit()
db.close()