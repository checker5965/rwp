from cs50 import SQL
import os
import smtplib
import random
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///ruhi.db")


@app.route("/")
@login_required
def index():
    """Show Assigned Didi"""
    rows = db.execute("SELECT * FROM tutees WHERE tid = :i", i = session["user_id"])
    if rows:
        for row in rows:
            didif=row['didif']
            didil=row['didil']
            team=row['type']
            number=row['number']
        return render_template("index.html", didif = didif, didil=didil, number = number, team=team)
    else:
        return render_template("index.html", didif = "NONE", didil="-", number = "-", team="-")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM tutors WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        if rows[0]['cnf']!=1:
            return apology("confirm your account", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/report", methods=["GET", "POST"])
@login_required
def report():
    """Submit Report."""
    if request.method == "GET":
        return render_template("report.html")
    else:
        rows=db.execute("SELECT * FROM tutors WHERE id = :i", i=session["user_id"])
        u=rows[0]["username"]
        db.execute("INSERT INTO reports(uid, username, report) VALUES(:i, :u, :r)", i=session["user_id"], u=u, r=request.form.get("report"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        message = u + " has just sent a report for Ruhi. Here is the report - \n\n" + request.form.get("report")
        server.login("ruhi@ashoka.edu.in", os.getenv("PASSWORD"))
        server.sendmail("ruhi@ashoka.edu.in", "priyanka.shankar_ug19@ashoka.edu.in", message)
        return render_template("success.html", string = "submitted the Report!")

@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    """Submit Report."""
    if request.method == "GET":
        return render_template("feedback.html")
    else:
        rows=db.execute("SELECT * FROM tutors WHERE id = :i", i=session["user_id"])
        u=rows[0]["username"]
        db.execute("INSERT INTO Feedback(uid, username, feedback) VALUES(:i, :u, :f)", i=session["user_id"], u=u, f=request.form.get("feedback"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        message = u + " has just sent a feedback for Ruhi. Here is the feedback - \n\n" + request.form.get("feedback")
        server.login("ruhi@ashoka.edu.in", os.getenv("PASSWORD"))
        server.sendmail("ruhi@ashoka.edu.in", "nethra.palepu_ug19@ashoka.edu.in", message)
        server.sendmail("ruhi@ashoka.edu.in", "sanjna.mishra_ug19@ashoka.edu.in", message)
        server.sendmail("ruhi@ashoka.edu.in", "esha.bafna_ug20@ashoka.edu.in", message)
        return render_template("success.html", string = "submitted the Feeback!")

@app.route("/bas", methods=["GET", "POST"])
@login_required
def bas():
    return render_template("bas.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        rows = db.execute("SELECT * FROM tutors WHERE username = :username", username=request.form.get("username"))
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not request.form.get("confirmation"):
            return apology("must provide confirmed password", 403)

        elif not len(request.form.get("password"))>=6:
            return apology("password must be at least 6 characters long", 403)

        elif not request.form.get("first"):
            return apology("must provide first name", 403)

        elif not request.form.get("last"):
            return apology("must provide last name", 403)

        elif not request.form.get("number"):
            return apology("must provide phone number", 403)

        elif not request.form.get("email"):
            return apology("must provide E-mail id", 403)

        elif not request.form.get("dorm"):
            return apology("must provide dorm", 403)

        elif not request.form.get("batch"):
            return apology("must provide batch", 403)

        elif len(rows) == 1:
            return apology("Username already exists", 403)

        elif len(db.execute("SELECT * FROM tutors WHERE email = :email", email=request.form.get("email"))) == 1:
            return apology("E-mail ID already registered", 403)

        else:
            sflag = "@ashoka.edu.in"
            sori=""
            c1 = 0
            for i in request.form.get("email"):
                if i == '@':
                    sori=request.form.get("email")[c1:len(request.form.get("email"))+1]
                    break
                c1+=1
            if sori != sflag:
                return apology("use ashoka e-mail id", 403)
            c2 = 0
            for i in request.form.get("number"):
                c2+=1
            if c2!=10:
                return apology("number incorrect")
            unassigned = db.execute("SELECT * FROM tutees where assigned = 0")
            if (not unassigned):
                return apology("All didis already assigned")
            h = generate_password_hash(request.form.get("password"), method = 'pbkdf2:sha256', salt_length=8)
            db.execute("INSERT INTO tutors(username, first, last, email, number, dorm, batch, password) VALUES(:username, :first, :last, :email, :number, :dorm, :batch, :password)", username=request.form.get("username"), first=request.form.get("first"), last=request.form.get("last"), email=request.form.get("email"), number=request.form.get("number"), dorm=request.form.get("dorm"), batch=request.form.get("batch"), password=h)
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            name = request.form.get("first")
            code = random.randint(100000,999999)
            db.execute("UPDATE tutors SET cnfcode = :cnfcode WHERE username = :username", cnfcode=str(code), username=request.form.get("username"))
            message = "Dear " + name + ",\n\nThank you for registering for Ruhi. Kindly find the confirmation code here - " + str(code) +"\n\nPlease enter this code here to confirm - http://ide50-ruhi2018.cs50.io:8080/confirm"
            server.login("ruhi@ashoka.edu.in", os.getenv("PASSWORD"))
            server.sendmail("ruhi@ashoka.edu.in", request.form.get("email"), message)
            return redirect("/confirm")
    else:
        return render_template("register.html")

@app.route("/confirm", methods=["GET", "POST"])
def confirm():
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM tutors WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        if rows[0]['cnf']==1:
            return apology("Already Confirmed! Use Login.")

        if rows[0]['cnfcode']!=request.form.get("cnfcode"):
            return apology("Wrong Verification Code", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        db.execute("UPDATE tutors SET cnf = 1 WHERE username = :username", username=request.form.get("username"))
        unassigned = db.execute("SELECT * FROM tutees WHERE assigned = 0")
        if (unassigned):
            didid=unassigned[0]['id']
            db.execute("UPDATE tutees SET tid = :i, assigned =1 WHERE id = :didid", i=session["user_id"], didid=didid)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("confirm.html")

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)