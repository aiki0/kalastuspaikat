import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session, make_response, flash
import config
import items
import users
import markupsafe

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

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)


@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    classes = items.get_classes(item_id)
    comments = items.get_comments(item_id)
    images = items.get_images(item_id) 
    return render_template("show_item.html", item=item, classes=classes, comments=comments, images=images)

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
    return render_template("new_item.html", classes=classes)



@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()

    comment = request.form["comment"]
    if len(comment) < 3:
        return render_template("new_item.html", error="Kommentin tulee olla vähintään 3 merkkiä pitkä")
    if len(comment) > 500:
        return render_template("new_item.html", error="Kommentin tulee olla enintään 500 merkkiä pitkä")

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
    return render_template("edit_item.html", item=item, classes=classes, all_classes=all_classes)

@app.route("/images/<int:item_id>")
def edit_images(item_id):
    require_login()
    item = items.get_item(item_id)
    if item is None:
        abort(404)
    if item["username"] != session["username"]:
        abort(403)
    images = items.get_images(item_id)
    return render_template("images.html", item=item, images=images)        

@app.route("/add_image", methods=["POST"])
def add_image():
    require_login()
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
            return redirect("/")
        else:
            flash("VIRHE: väärä tunnus tai salasana")
            return redirect("/login")
@app.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
    return redirect("/")