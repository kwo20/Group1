from flask import Flask, render_template, redirect, url_for, request, jsonify
import json
import sqlite3
import random
current_user = "test"
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
    return redirect("/login")

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
        return render_template('login.html')
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
            global current_user
            current_user = request.form['username']
            return redirect('/frontpage')
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/frontpage', methods=['GET', 'POST'])
def post():
    global current_user
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM posts WHERE username=? ORDER BY id DESC""", (current_user,))
    list2 = []
    for row in cursor.fetchall():
            list2.append(row)
    if not list2:
        cursor.execute("""SELECT * FROM posts WHERE id=12""")
        for row in cursor.fetchall():
            list2.append(row)
            
        
    if request.method == 'POST':
        new_post = request.form['post-input']
        sql = """INSERT INTO posts (content, username)
                VALUES (?, ?)"""
        cursor = cursor.execute(sql, (new_post, current_user))
        conn.commit()
        sql1 = """SELECT * FROM posts WHERE username=? ORDER BY id DESC"""
        cursor.execute(sql1, (current_user,))
        list2.clear()
        for row in cursor.fetchall():
            list2.append(row)
        return render_template('frontpage.html', user=current_user, postlist = list2)
    else:
        return render_template('frontpage.html', user=current_user, postlist = list2)
    
@app.route('/search', methods=['GET', 'POST'])       
def search():
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        new_search = request.form['username']
        sql = """SELECT username FROM users WHERE username=?"""
        cursor.execute(sql, (new_search,))
        test = cursor.fetchone()
        if not test:
            return render_template('search.html')
        elif test: 
            return render_template('mainpage.html')
    else:
        return render_template('search.html')
    
if __name__ == "__main__":
    app.run(debug=True)

    
