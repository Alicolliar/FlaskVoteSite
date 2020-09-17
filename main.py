from flask import Flask, render_template, url_for, request, redirect
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import pymysql as sql
import datetime, time
app = Flask(__name__)
db = sql.connect(
    host="""Enter the hostname of your database here""",
    user="""Enter the username of your mysql here""",
    password="""Enter the password for the above user here""",
    db="""Enter the database name of the database you want to use here""")
@app.route('/')
def home():
    t = datetime.datetime.now()
    print(t)
    unixtime = t.timestamp()
    print(unixtime)
    query = "SELECT electID, question, ending FROM elects WHERE running = 1"
    with db.cursor() as cursor:
        cursor.execute(query)
        db.commit()
        foundPwd = cursor.fetchone()
    print(foundPwd)
    if not foundPwd:
        return render_template("home.html")
    if 2 == unixtime:
        query2 = "UPDATE elects SET running = 0 WHERE electID = %s"
        with db.cursor() as cursor:
            cursor.execute(query2, foundPwd[0])
            db.commit()
    return render_template("home.html", currElect=foundPwd)

@app.route('/voting', methods=["GET", "POST"])
def voting():
    if request.method == "POST":
        requ = request.form
        if "login" in requ:
            uname = requ["uname"]
            pwd = requ["pwd"]
            query = "SELECT userID, pwd, voted FROM users WHERE username = %s"
            with db.cursor() as cursor:
                cursor.execute(query, uname)
                db.commit()
                foundPwd = cursor.fetchone()
            if not foundPwd:
                return render_template("voting.html", logMessage="Incorrect Username")
            elif pwd == foundPwd[1]:
                query2 = "SELECT electID, question FROM elects WHERE running = 1;"
                query3 = "UPDATE users SET voted = 1 WHERE userID = %s;"
                with db.cursor() as cursor:
                    cursor.execute(query2)
                    cursor.execute(query3, foundPwd[0])
                    cursor.execute(query2)
                    db.commit()
                    foundPwd2 = cursor.fetchone()
                if not foundPwd2:
                    return render_template("voting.html", logMessage="No election running currently")
                toAsk = "Election ID: "+str(foundPwd2[0])+". "+foundPwd2[1]
                return render_template("voting.html", question=toAsk)
            elif foundPwd[2] == 1:
                return render_template("voting.html", logMessage="You Have Already Voted In This Election")

        elif "voting" in requ:
            choice = requ["vote"]
            query1 = "SELECT yes, negative FROM elects WHERE running = 1;"
            with db.cursor() as cursor:
                cursor.execute(query1)
                db.commit()
                yesesandnoes = cursor.fetchone()
            if choice == "yes":
                total = yesesandnoes[0]+1
                query = "UPDATE elects SET yes = %s"
            elif choice == "no":
                total = yesesandnoes[1]+1
                query = "UPDATE elects SET negative = %s"
            with db.cursor() as cursor:
                cursor.execute(query, total)
                db.commit()

    return render_template("voting.html")

@app.route('/archive')
def archive():
    with db.cursor() as cursor:
        query = "SELECT question, yes, negative FROM elects WHERE running = 0;"
        cursor.execute(query)
        db.commit()
        foundData = cursor.fetchall()
        print(foundData)
    return render_template("archive.html", foundData=foundData)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        req = request.form
        print(req)
        uname = req["uname"]
        pwd = req["password"]
        query = "SELECT pwd, userLevel FROM users WHERE username = %s"
        with db.cursor() as cursor:
            cursor.execute(query, uname)
            db.commit()
            foundPwd = cursor.fetchone()
        print(foundPwd)
        if not foundPwd:
            return render_template("login.html", message="Incorrect Username")
        elif foundPwd[1] != 1:
            return render_template("login.html", message="Incorrect User Level")
        elif pwd == foundPwd[0]:
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", message="Incorrect Password")
    return render_template("login.html")

@app.route('/83059', methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        input = request.form
        if "electMake" in input:
            quest = input["question"]
            startTime = datetime.datetime.now()
            startText = startTime.strftime("%y-%m-%dT%H:%M")
            end = str(input["endDate"])
            toSend = (quest, startText, end)
            print(toSend)
            query = "INSERT INTO elects (question, beginning, ending, running, yes, negative) VALUES (%s, %s, %s, 1, 0, 0)"
            with db.cursor() as cursor:
                cursor.execute(query, toSend)
                db.commit()
                message= "Election asking \""+quest+"\" has been started."
                return render_template("admin.html", message=message)
        elif "electCancel" in input:
            query = "UPDATE elects SET running = 0 WHERE running = 1;"
            with db.cursor() as cursor:
                cursor.execute(query)
                db.commit()
            return render_template("admin.html", message="Election Cancelled.")
        elif "userAdd" in input:
            username = input["user"]
            password = input["pwd"]
            level = input["level"]
            toSend = (username, password)
            if level == "1":
                query = "INSERT INTO users (username, pwd, userLevel) VALUES (%s, %s, 1);"
                ulevel = "n admin"
            else:
                query = "INSERT INTO users (username, pwd, userLevel) VALUES (%s, %s, 0);"
                ulevel = " voter"
            with db.cursor() as cursor:
                cursor.execute(query, toSend)
                db.commit()
                message = "User "+username+" added to database as a"+ulevel
                return render_template("admin.html", message=message)

    return render_template("admin.html")

if __name__ == '__main__':
    app.run(debug=True)
