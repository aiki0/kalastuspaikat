import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session
import db
import config
import items
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "username" not in session:
        abort(403)

@app.route("/")
def index():
    all_items = items.get_items()
    return render_template("index.html", items=all_items)

@app.route("/user/<username>")
def show_user(username):
    user = users.get_user(username)
    if user is None:
        abort(404) 
    user_items = users.get_items(username)

    return render_template("show_user.html", user=user, items=user_items)


@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    classes = items.get_classes(item_id)
    return render_template("show_item.html", item=item, classes=classes)

@app.route("/new_item")
def new_item():
    if "username" not in session:
        return redirect("/login")
    require_login()
    classes = items.get_all_classes()
    return render_template("new_item.html", classes=classes)

@app.route("/create_item", methods=["POST"])
def create_item():
    require_login()
    title = request.form["title"]
    if len(title) < 3:
        return render_template("new_item.html", error="Otsikon tulee olla vähintään 3 merkkiä pitkä")
    if len(title) > 45:
        return render_template("new_item.html", error="Otsikon tulee olla enintään 45 merkkiä pitkä")
    description = request.form["description"]
    if len(description) > 1000:
        return render_template("new_item.html", error="Kuvauksen tulee olla enintään 1000 merkkiä pitkä")
    username = session["username"]
    
    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            key, value = entry.split(":", 1)
            classes.append((key.strip(), value.strip()))
    items.add_item(title, description, username, classes)
    return redirect("/")

@app.route("/update_item", methods=["POST"])
def update_item():
    require_login()
    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    if item["username"] != session["username"]:
        abort(403)
    title = request.form["title"]
    if len(title) < 3:
        abort(400, "Otsikon tulee olla vähintään 3 merkkiä pitkä")
    if len(title) > 45:
        abort(400, "Otsikon tulee olla enintään 45 merkkiä pitkä")

    description = request.form["description"]

    items.update_item(item_id, title, description)
    return redirect("/item/" + item_id)


@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    require_login()
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    if item["username"] != session["username"]:
        return redirect("/")
    return render_template("edit_item.html", item=item)

@app.route("/remove_item/<int:item_id>", methods=["GET", "POST"])
def remove_item(item_id):
    require_login()
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
    try:
        users.create_user(username, password1)
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
        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
    return redirect("/")