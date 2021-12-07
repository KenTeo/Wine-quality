from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta, datetime
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import MySQLdb.cursors
import pandas as pd
import pickle
import yaml
import os
import io
import csv


app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=15)

db = yaml.safe_load(open('templates/db.yml'))
app.secret_key = db['secret_key']
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)


def quality_predict(df):
    with open("model.bin", 'rb') as f_in:
        model = pickle.load(f_in)

    prediction = model.predict(df)
    return prediction


def save_data(df, y, user):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    df["predicted quality"] = y
    df.insert(0,"time_date", now)
    df.insert(0, "user", user)
    cursor = mysql.connection.cursor()

    for i in range(0, len(df)):
        sql = "INSERT INTO wine_prop VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val = (user, now, df["fixed acidity"][i],df["volatile acidity"][i],df["citric acid"][i],df["free sulfur dioxide"][i],
               df["total sulfur dioxide"][i],df["density"][i],df["pH"][i],df["sulphates"][i],df["alcohol"][i],y[i])
        cursor.execute(sql, val)
    mysql.connection.commit()
    return

def wrong_format(filename):
    if not "." in filename:
        return True
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() == "CSV":
        return False
    else:
        return True


def data_limit():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    no_rows = cursor.execute('SELECT * FROM wine_prop')
    return no_rows


@app.route("/", methods=["POST", "GET"])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            flash('Logged in successfully!')
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)


@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash("You have successfully logged out!")
    return redirect(url_for('login'))


@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        elif cursor.execute('SELECT * FROM accounts;') >= 100:
            msg = 'Maximum account limit has been reached! Please use Username: testuser, Password: pass instead!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app.route("/home")
def home():
    if session:
        cursor = mysql.connection.cursor()
        resultvalue = cursor.execute("SELECT * FROM wine_prop")
        wine_list = []
        if resultvalue > 0:
            wine_list = cursor.fetchall()
        return render_template("home.html", wine_list=wine_list[::-1])
    else:
        return redirect(url_for("login"))


@app.route("/quick", methods =['GET', 'POST'])
def quick():
    if session:
        if request.method == "POST":
            fixed_acidity = float(request.form['fixed acidity'])
            volatile_acidity = float(request.form['volatile acidity'])
            citric_acid = float(request.form['citric acid'])
            free_sulfur_dioxide = float(request.form['free sulfur dioxide'])
            total_sulfur_dioxide = float(request.form['total sulfur dioxide'])
            density = float(request.form['density'])
            ph = float(request.form['ph'])
            sulphates = float(request.form['sulphates'])
            alcohol = float(request.form['alcohol'])

            df = pd.DataFrame({
                "fixed acidity": [fixed_acidity],
                "volatile acidity": [volatile_acidity],
                "citric acid": [citric_acid],
                "free sulfur dioxide": [free_sulfur_dioxide],
                "total sulfur dioxide": [total_sulfur_dioxide],
                "density": [density],
                "pH": [ph],
                "sulphates": [sulphates],
                "alcohol": [alcohol],
            })
            df = pd.DataFrame(df)
            prediction = quality_predict(df)
            if data_limit() > 8999:
                msg = 'Data limit reached. Prediction data not saved.'
                return render_template("quick.html", prediction=prediction, msg=msg)
            else:
                username = session['username']
                save_data(df, prediction, username)
                msg = "Prediction data saved."
                return render_template("quick.html", prediction=prediction, msg=msg)
        else:
            return render_template("quick.html")
    else:
        return redirect(url_for("login"))


@app.route("/mass", methods=['GET', 'POST'])
def mass():
    if session:
        if request.method == "POST":
            if request.files:
                data_file = request.files["customFile"]
                if data_file.filename == "":
                    msg = "No file uploaded"
                    return render_template("mass.html", msg=msg)
                filename = secure_filename(data_file.filename)
                if wrong_format(filename):
                    msg = "Wrong file format"
                    return render_template("mass.html", msg=msg)
                stream = io.StringIO(data_file.stream.read().decode("UTF8"))
                csv_input = csv.DictReader(stream, delimiter=',')
                df = pd.DataFrame(csv_input)
                required_columns = ['fixed acidity', 'volatile acidity', 'citric acid', 'free sulfur dioxide',
                                   'total sulfur dioxide', 'density', 'pH','sulphates', 'alcohol']
                if (data_limit()+len(df)) > 9000:
                    msg = 'Data limit reached. This feature is not available.'
                    return render_template("mass.html", msg=msg)
                if not ((df.columns.values == required_columns).all()):
                    msg = "Columns are missing, misspelled or wrongly sorted. See reference above"
                    return render_template("mass.html", msg=msg)
                if df.eq('').any().any():
                    msg = "There are missing values in your data. Please fill in all values."
                    return render_template("mass.html", msg=msg)
                prediction = quality_predict(df)
                username = session['username']
                save_data(df, prediction, username)
                flash("Data from CSV file has been saved")
                return redirect(url_for("home"))
        return render_template("mass.html")
    else:
        return redirect(url_for("login"))
