import sqlite3
from flask import Flask
import math
from flask import abort, redirect, render_template, request, session, make_response, flash
import config
import items
import users
import markupsafe
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "username" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/<int:page>")
@app.route("/", defaults={"page": 1})
def index(page):
    page_size = 10
    item_count = items.item_count()
    page_count = math.ceil(item_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect(f"/{page_count}")

    all_items = items.get_items(page, page_size)
    return render_template("index.html", page=page, page_count=page_count, items=all_items)

@app.route("/user/<username>")
@app.route("/user/<username>/<int:page>")
def show_user(username, page=1):
    user = users.get_user(username)
    if user is None:
        abort(404)

    page_size = 10
    total_items = users.item_count(username)
    item_count = users.item_count(username)
    page_count = math.ceil(item_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect(f"/user/{username}/1")
    if page > page_count:
        return redirect(f"/user/{username}/{page_count}")

    user_items = users.get_items(username, page, page_size)
    return render_template(
        "show_user.html",
        user=user,
        items=user_items,
        page=page,
        page_count=page_count,
        total_items=total_items,)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)


@app.route("/item/<int:item_id>/<int:page>")
@app.route("/item/<int:item_id>", defaults={"page": 1})
def show_item(item_id, page):
    item = items.get_item(item_id)
    if item is None:
        abort(404)

    classes = items.get_classes(item_id)
    images = items.get_images(item_id)

    page_size = 6
    comment_count = items.comment_count(item_id)
    page_count = math.ceil(comment_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/item/"+ str(item_id) + "/1")
    if page > page_count:
        return redirect("/item/"+ str(item_id) + "/" + str(page_count))

    comments = items.get_comments(item_id, page, page_size)

    return render_template(
        "show_item.html",
        item=item,
        classes=classes,
        comments=comments,
        images=images,
        page=page,
        page_count=page_count,)

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = items.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response


@app.route("/new_item")
def new_item():
    if "username" not in session:
        return redirect("/login")
    require_login()
    classes = items.get_all_classes()
    return render_template(
        "new_item.html",
        classes=classes)



@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()
    check_csrf()

    comment = request.form["comment"]
    if not comment or len(comment) > 101:
        abort(403)

    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(403)

    username = session["username"]
    user = users.get_user(username)
    if not user:
        abort(403)

    items.add_comment(comment, user["id"], item_id)  
    return redirect("/item/" + str(item_id))

@app.route("/create_item", methods=["POST"])
def create_item():
    require_login()
    check_csrf()
    title = request.form["title"]
    description = request.form["description"]
    if not title or len(title) > 46:
        abort(403)
    if not description or len(description) > 1000:
        abort(403)
    username = session["username"]
    all_classes = items.get_all_classes()
    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))
    items.add_item(title, description, username, classes)
    return redirect("/")

@app.route("/update_item", methods=["POST"])
def update_item():
    require_login()
    check_csrf()
    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    if item["username"] != session["username"]:
        abort(403)
    title = request.form["title"]
    description = request.form["description"]
    if not title or len(title) > 46:
        abort(403)
    if not description or len(description) > 1000:
        abort(403)
    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            key, value = entry.split(":", 1)
            classes.append((key.strip(), value.strip()))
    items.update_item(item_id, title, description, classes)
    return redirect("/item/" + item_id)


@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    require_login()
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    if item["username"] != session["username"]:
        return redirect("/")
    all_classes = items.get_all_classes()
    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))
    return render_template(
        "edit_item.html",
        item=item,
        classes=classes, 
        all_classes=all_classes)

@app.route("/images/<int:item_id>")
def edit_images(item_id):
    require_login()
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    if item["username"] != session["username"]:
        abort(403)
    images = items.get_images(item_id)
    return render_template(
        "images.html",
        item=item,
        images=images)        

@app.route("/add_image", methods=["POST"])
def add_image():
    require_login()
    check_csrf()
    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    if item["username"] != session["username"]:
        abort(403)

    file = request.files["image"]
    if not file.filename.endswith(".png"):
        return "VIRHE: väärä tiedostomuoto"

    image = file.read()
    if len(image) > 100 * 1024:
        return "VIRHE: liian suuri kuva"

    items.add_image(item_id, image)
    return redirect("/images/" + str(item_id))

@app.route("/remove_images", methods=["POST"])
def remove_images():
    require_login()
    check_csrf()
    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    if item["username"] != session["username"]:
        abort(403)

    for image_id in request.form.getlist("image_id"):
        items.remove_image(image_id, item_id)

    return redirect("/images/" + str(item_id))

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
            return render_template(
                "remove_item.html",
                item=item)
        if request.method == "POST":
            check_csrf()
            if "remove" in request.form:
                items.remove_item(item_id)
                return redirect("/")
            else:
                return redirect("/item/" + str(item_id)) 
            
@app.route("/find_items", methods=["GET", "POST"])
def finditems():
    query = request.args.get("query") or ""
    all_items = items.find_items(query)
    return render_template(
        "find_items.html",
        items=all_items,
        query=query)
            

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])

def create():
    username = request.form.get("username", "").strip()
    password1 = request.form.get("password1", "").strip()
    password2 = request.form.get("password2", "").strip()
    if not username:
        flash("VIRHE: Käyttäjätunnus ei voi olla tyhjä")
        return render_template("register.html", username=username)

    if password1 != password2:
        flash("VIRHE: Salasanat eivät ole samat")
        return render_template("register.html", username=username)

    if not password1 or not password2:
        flash("VIRHE: Salasana ei voi olla tyhjä")
        return render_template("register.html", username=username)

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: tunnus on jo varattu")
        return render_template("register.html", username=username)

    flash("Käyttäjä luotu! Kirjaudu sisään.")
    return redirect("/login")

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
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("VIRHE: väärä tunnus tai salasana")
            return redirect("/login")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")