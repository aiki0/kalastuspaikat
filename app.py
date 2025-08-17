import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import items

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_items = items.get_items()
    return render_template("index.html", items=all_items)

@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    return render_template("show_item.html", item=item)

@app.route("/new_item")
def new_item():
    return render_template("new_item.html")

@app.route("/create_item", methods=["POST"])
def create_item():
    title = request.form["title"]
    description = request.form["description"]
    username = session["username"]

    items.add_item(title, description, username)
    return redirect("/")

@app.route("/update_item", methods=["POST"])
def update_item():
    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    if item["username"] != session["username"]:
        abort(403)
    title = request.form["title"]
    description = request.form["description"]

    items.update_item(item_id, title, description)
    return redirect("/item/" + item_id)


@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    if item["username"] != session["username"]:
        return redirect("/")
    return render_template("edit_item.html", item=item)

@app.route("/remove_item/<int:item_id>", methods=["GET", "POST"])
def remove_item(item_id):
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    if item["username"] != session["username"]:
        return redirect("/")
    else:
        if request.method == "GET":
            return render_template("remove_item.html", item=item)
        if request.method == "POST":
            if "remove" in request.form:
                items.remove_item(item_id)
                return redirect("/")
            else:
                return redirect("/item/" + str(item_id)) 
            
@app.route("/find_items", methods=["GET", "POST"])
def finditems():
    query = request.args.get("query") or ""
    all_items = items.find_items(query)
    return render_template("find_items.html", items=all_items, query=query)
            

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return redirect("/")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        
        sql = "SELECT password_hash FROM users WHERE username = ?"
        password_hash = db.query(sql, [username])[0][0]

        if check_password_hash(password_hash, password):
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")