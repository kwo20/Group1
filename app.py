from flask import Flask, render_template, redirect, url_for, request, jsonify
import json
import sqlite3

app = Flask(__name__)

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("bickerdb.sqlite")
    except sqlite3.error as e:
        print(e)
    return conn

@app.route('/')
def index():
    return render_template('frontpage.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        sql = """INSERT INTO users (username, password)
                 VALUES (?, ?)"""
        
        cursor = cursor.execute(sql, (new_username, new_password))
        conn.commit()
        return render_template('frontpage.html')
    else:
        return render_template('create.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        cursor.execute("""SELECT password FROM users WHERE username=?""", (request.form['username'],))
        test = cursor.fetchone()
        if not test:
            return render_template('login.html')
        elif test[0] == request.form['password']:
            return render_template('mainpage.html')
        else:
            return render_template('login.html')
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
