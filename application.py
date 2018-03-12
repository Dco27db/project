from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///comedy.db")

@app.route("/addComedian", methods = ["GET", "POST"])
@login_required
def addComedian():
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # checks that user provided the name of a comedian to add
        if not request.form.get("comedian"):
            return apology("Provide the name of a comedian!")

        # checks comedian input for restricted characters
        try:
            if "'" in request.form.get("comedian"):
                raise "special characters alert"
            elif ";" in request.form.get("comedian"):
                raise "special characters alert"
        except:
                return apology("No special characters!")

        # adds comedian name to the user's myComedians list
        rows = db.execute("INSERT INTO myComedians (user_id_comedy,comedian_name) VALUES(:user_id, :comedian_name)",
        user_id = session["user_id"], comedian_name = request.form.get("comedian"))
        if not rows:
            return apology("Comedian already on My Comedians List!")

        # redirect to the user's myComedians list
        return redirect(url_for("myComedians"))

    # else if user reached via GET
    elif request.method == "GET":
        return render_template("addComedian.html")

@app.route("/addContent", methods = ["GET", "POST"])
@login_required
def addContent():
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # checks that user filled every field in the html form
        if not request.form.get("comedian"):
            return apology("Provide the name of a comedian!")
        if not request.form.get("contentName"):
            return apology("Provide the name of the content!")
        if not request.form.get("contentType"):
            return apology("Specify the type of content!")
        if not request.form.get("contentSource"):
            return apology("Provide the source of the content!")
        if not request.form.get("contentDate"):
            return apology("Provide the date of the content!")
        if not request.form.get("contentLink"):
            return apology("Provide the link to the content!")

        # checks the input for every field in the form for restricted characters
        fields = ["comedian", "contentName", "contentType", "contentSource", "contentDate", "contentLink"]
        try:
            for field in fields:
                if "'" in request.form.get(field):
                    raise "special characters alert"
                elif ";" in request.form.get(field):
                    raise "special characters alert"
        except:
                return apology("No special characters!")

        # checks that the comedian name is in the user's list of my Comedians (consider just automatically adding name to my comedians list, if not there)
        rows = db.execute("SELECT comedian_name FROM myComedians WHERE user_id_comedy = :user_id and comedian_name = :comedian_name",
        user_id = session["user_id"], comedian_name = request.form.get("comedian"))
        print("ATTENTION", rows)
        # this will also be triggered if the database's unique constraint on the contentLink column is violated
        if not rows:
            return apology("Comedian not on My Comedians List. Please Add!")

        # adds comedian name to the user's myComedians list
        rows = db.execute("INSERT INTO myContent (user_id_content,comedian_name,content_name,content_type,\
        content_source,content_date,content_link) VALUES(:user_id, :comedian_name, :content_name, :content_type, :content_source,\
        :content_date, :content_link)",
        user_id = session["user_id"], comedian_name = request.form.get("comedian"),content_name = request.form.get("contentName"),
        content_type = request.form.get("contentType"), content_source = request.form.get("contentSource"), content_date =
        request.form.get("contentDate"), content_link = request.form.get("contentLink"))
        if not rows:
            return apology("This content is already on My Content list!")

        # redirect to the user's myComedians list
        return redirect(url_for("myContent"))

    # else if user reached via GET
    elif request.method == "GET":
        return render_template("addContent.html")

@app.route("/dropComedian", methods = ["GET", "POST"])
@login_required
def dropComedian():

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # checks the the user provided the name of a comedian to drop
        if not request.form.get("comedian"):
            return apology("Provide the name of a comedian!")

        # checks comedian input for restricted characters
        try:
            if "'" in request.form.get("comedian"):
                raise "special characters alert"
            elif ";" in request.form.get("comedian"):
                raise "special characters alert"
        except:
                return apology("No special characters!")

        # checks that the comedian name is on the user's myComedians list
        rows = db.execute("SELECT comedian_name FROM myComedians WHERE user_id_comedy = :user_id and comedian_name = :comedian_name",
        user_id = session["user_id"], comedian_name = request.form.get("comedian"))

        # returns apology if the comedian is already on the user's myComedians list
        if not rows:
            return apology("Comedian not on myComedians list!")

        rows = db.execute("DELETE FROM myComedians WHERE user_id_comedy = :user_id and comedian_name = :comedian_name",
        user_id = session["user_id"], comedian_name = request.form.get("comedian"))

        # redirect to the user's myComedians list
        return redirect(url_for("myComedians"))

    # else if user reached via GET
    elif request.method == "GET":
        return render_template("dropComedian.html")

@app.route("/dropContent", methods = ["GET", "POST"])
@login_required
def dropContent():
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # checks that the user provided a link to the content to drop
        if not request.form.get("contentLink"):
            return apology("Provide a link to the content to drop!")

        # checks that the contentLink input doesn't contain restricted characters
        try:
            if "'" in request.form.get("contentLink"):
                raise "special characters alert"
            elif ";" in request.form.get("contentLink"):
                raise "special characters alert"
        except:
                return apology("No special characters!")

        # deletes the specified content from the user's myContent list
        rows = db.execute("DELETE FROM myContent WHERE user_id_content = :user_id and content_link = :content_link",
        user_id = session["user_id"], content_link = request.form.get("contentLink"))

        # returns apology if the content can't be found on the user's myContent list
        if not rows:
            return apology("Content not found on My Content list!")

        # redirect to the user's myComedians list
        return redirect(url_for("myComedians"))

    # else if user reached via GET
    elif request.method == "GET":
        return render_template("dropContent.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # checks username and password input for restricted characters
        try:
            if "'" in request.form.get("username"):
                raise "special characters alert"
            elif ";" in request.form.get("username"):
                raise "special characters alert"
            elif "'" in request.form.get("password"):
                raise "special characters alert"
            elif ";" in request.form.get("password"):
                raise "special characters alert"
        except:
                return apology("No special characters!")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # redirect user to home page
        return redirect(url_for("myComedians"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/")
@login_required
def myComedians():

    # retrieves username
    user = db.execute("SELECT * FROM users WHERE user_id = :id", id = session["user_id"])

    # retrieves comedian names
    comedians = db.execute("SELECT comedian_name FROM myComedians WHERE user_id_comedy = :id", id = session["user_id"])

    return render_template("myComedians.html",
    username = user[0]["username"], comedians = comedians)

@app.route("/myContent")
@login_required
def myContent():

    # retrives the user's id and the information from each column of the users myContent table
    user = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id = session["user_id"])
    comedian = db.execute("SELECT comedian_name FROM myContent WHERE user_id_content = :user_id", user_id = session["user_id"])
    contentName = db.execute("SELECT content_name FROM myContent WHERE user_id_content = :user_id", user_id = session["user_id"])
    contentType = db.execute("SELECT content_type FROM myContent WHERE user_id_content = :user_id", user_id = session["user_id"])
    contentSource = db.execute("SELECT content_source FROM myContent WHERE user_id_content = :user_id", user_id = session["user_id"])
    contentDate = db.execute("SELECT content_date FROM myContent WHERE user_id_content = :user_id", user_id = session["user_id"])
    contentLink = db.execute("SELECT content_link FROM myContent WHERE user_id_content = :user_id", user_id = session["user_id"])

    # create tuple of all transaction information (Note: the values have to be entered in their order used in the html file)
    contentInfo = zip(comedian, contentName, contentType, contentSource, contentDate, contentLink)

    return render_template("myContent.html", username = user[0]["username"], info=contentInfo)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # checks that the user provided a username
        if request.form.get("username") == "":
            return apology("Missing username!")

        # checks that the user provided a password and password confirmation, and that both match
        if request.form.get("password") == "":
            return apology("Missing password!")
        elif request.form.get("passwordc") == "":
            return apology("Missing password confirmation!")
        elif request.form.get("password") != request.form.get("passwordc"):
            return apology("Passwords do not match!")

        # checks username, password, and password confirmation input for restricted characters
        try:
            if "'" in request.form.get("username"):
                raise "special characters alert"
            elif ";" in request.form.get("username"):
                raise "special characters alert"
            elif "'" in request.form.get("password"):
                raise "special characters alert"
            elif ";" in request.form.get("password"):
                raise "special characters alert"
            elif "'" in request.form.get("passwordc"):
                raise "special characters alert"
            elif ";" in request.form.get("passwordc"):
                raise "special characters alert"
        except:
                return apology("No special characters!")

        # enters user information into database
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hashp)",
        username = request.form.get("username"), hashp = pwd_context.hash(request.form.get("password")))
        if not result:
            return apology("Username already taken!")

        # log new user in
        session["user_id"] = result
        return redirect(url_for("myComedians"))

    # else if user reached via GET
    elif request.method == "GET":
        return render_template("register.html")
