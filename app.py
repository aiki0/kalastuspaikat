import sqlite3
from flask import Flask
import math
from flask import abort, redirect, render_template, request, session, make_response, flash
import config
import places
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

@app.route("/", defaults={"page": 1})
@app.route("/<int:page>")
def index(page):
    page_size = 10
    query = request.args.get("query", default="", type=str)

    if query:
        place_count = places.count_places(query)
        all_places = places.find_places(query, page, page_size)
    else:
        place_count = places.place_count()
        all_places = places.get_places(page, page_size)

    page_count = max(math.ceil(place_count / page_size), 1)

    if page < 1:
        return redirect("/1?query=" + query)
    if page > page_count:
        return redirect(f"/{page_count}?query={query}")

    place_classes = {}
    for place in all_places:
        rows = places.get_classes(place["id"])
        place_classes[place["id"]] = [f"{row['title']}: {row['value']}" for row in rows]

    return render_template(
        "index.html",
        page=page,
        page_count=page_count,
        places=all_places,
        query=query,
        place_classes=place_classes)

@app.route("/user/<username>")
@app.route("/user/<username>/<int:page>")
def show_user(username, page=1):
    user = users.get_user(username)
    if user is None:
        abort(404)

    page_size = 10
    total_places = users.place_count(username)
    page_count = max(math.ceil(total_places / page_size), 1)

    if page < 1:
        return redirect(f"/user/{username}/1")
    if page > page_count:
        return redirect(f"/user/{username}/{page_count}")

    user_places = users.get_places(username, page, page_size)

    place_classes = {}
    for place in user_places:
        rows = places.get_classes(place["id"])
        place_classes[place["id"]] = [f"{row['title']}: {row['value']}" for row in rows]

    return render_template(
        "show_user.html",
        user=user,
        places=user_places,
        page=page,
        page_count=page_count,
        total_places=total_places,
        place_classes=place_classes)


@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/place/<int:place_id>/<int:page>")
@app.route("/place/<int:place_id>", defaults={"page": 1})
def show_place(place_id, page):
    place = places.get_place(place_id)
    if place is None:
        abort(404)

    classes = places.get_classes(place_id)
    images = places.get_images(place_id)

    page_size = 6
    comment_count = places.comment_count(place_id)
    page_count = math.ceil(comment_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/place/"+ str(place_id) + "/1")
    if page > page_count:
        return redirect("/place/"+ str(place_id) + "/" + str(page_count))

    comments = places.get_comments(place_id, page, page_size)

    return render_template(
        "show_place.html",
        place=place,
        classes=classes,
        comments=comments,
        images=images,
        page=page,
        page_count=page_count)

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = places.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response


@app.route("/new_place")
def new_place():
    if "username" not in session:
        return redirect("/login")
    require_login()
    classes = places.get_all_classes()
    return render_template(
        "new_place.html",
        classes=classes)



@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()
    check_csrf()

    comment = request.form["comment"]
    if not comment or len(comment) > 101:
        abort(403)

    place_id = request.form["place_id"]
    place = places.get_place(place_id)
    if not place:
        abort(403)

    username = session["username"]
    user = users.get_user(username)
    if not user:
        abort(403)

    places.add_comment(comment, user["id"], place_id)  
    return redirect("/place/" + str(place_id))

@app.route("/create_place", methods=["POST"])
def create_place():
    require_login()
    check_csrf()
    title = request.form["title"]
    description = request.form["description"]
    if not title or len(title) > 46:
        abort(403)
    if not description or len(description) > 1000:
        abort(403)
    username = session["username"]
    all_classes = places.get_all_classes()
    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))
    places.add_place(title, description, username, classes)
    return redirect("/")

@app.route("/update_place", methods=["POST"])
def update_place():
    require_login()
    check_csrf()
    place_id = request.form["place_id"]
    place = places.get_place(place_id)
    if place is None:
        abort(404)
    if place["username"] != session["username"]:
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
    places.update_place(place_id, title, description, classes)
    return redirect("/place/" + place_id)


@app.route("/edit_place/<int:place_id>")
def edit_place(place_id):
    require_login()
    place = places.get_place(place_id)
    if place is None:
        abort(404)
    if place["username"] != session["username"]:
        return redirect("/")
    all_classes = places.get_all_classes()
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
        "edit_place.html",
        place=place,
        classes=classes, 
        all_classes=all_classes)

@app.route("/images/<int:place_id>")
def edit_images(place_id):
    require_login()
    place = places.get_place(place_id)
    if place is None:
        abort(404)
    if place["username"] != session["username"]:
        abort(403)
    images = places.get_images(place_id)
    return render_template(
        "images.html",
        place=place,
        images=images)        

@app.route("/add_image", methods=["POST"])
def add_image():
    require_login()
    check_csrf()
    place_id = request.form["place_id"]
    place = places.get_place(place_id)
    if place is None:
        abort(404)
    if place["username"] != session["username"]:
        abort(403)

    all_images = places.get_images(place_id)
    if len(all_images) >= 3:
        return "VIRHE: liian monta kuvaa (max 3)"

    file = request.files["image"]
    if not file.filename.endswith(".png"):
        return "VIRHE: väärä tiedostomuoto"

    image = file.read()
    if len(image) > 100 * 1024:
        return "VIRHE: liian suuri kuva"

    places.add_image(place_id, image)
    return redirect("/images/" + str(place_id))

@app.route("/remove_images", methods=["POST"])
def remove_images():
    require_login()
    check_csrf()
    place_id = request.form["place_id"]
    place = places.get_place(place_id)
    if place is None:
        abort(404)
    if place["username"] != session["username"]:
        abort(403)

    for image_id in request.form.getlist("image_id"):
        places.remove_image(image_id, place_id)

    return redirect("/images/" + str(place_id))

@app.route("/remove_place/<int:place_id>", methods=["GET", "POST"])
def remove_place(place_id):
    require_login()
    place = places.get_place(place_id)
    if place is None:
        abort(404)
    if place["username"] != session["username"]:
        return redirect("/")
    else:
        if request.method == "GET":
            return render_template(
                "remove_place.html",
                place=place)
        if request.method == "POST":
            check_csrf()
            if "remove" in request.form:
                places.remove_place(place_id)
                return redirect("/")
            else:
                return redirect("/place/" + str(place_id)) 

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
    
    if len(username) > 20:
        flash("VIRHE: Käyttäjätunnus on liian pitkä (max 20 merkkiä)")
        return render_template("register.html")

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