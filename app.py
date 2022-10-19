from flask import Flask, render_template, redirect, url_for, request, jsonify
import json
import sqlite3
import random
current_user = "test"
current_page = "null"
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
        return redirect("/login")
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
    global current_page
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT id, content, username, created_at, follower_name
                  FROM posts
                  INNER JOIN followers ON username=followed_name
                  WHERE follower_name=?
                  UNION ALL
                  SELECT id, content, username, created_at, 'blank' AS follower_name
                  FROM posts
                  WHERE username=?
                  ORDER BY id DESC""", (current_user, current_user))
    list2 = []
    for row in cursor.fetchall():
            list2.append(row)
    if not list2:
        cursor.execute("""SELECT * FROM posts WHERE id=12""")
        for row in cursor.fetchall():
            list2.append(row)
            
        
    if request.method == 'POST':
        if request.form.get("post-input") is not None:
            new_post = request.form['post-input']
            sql = """INSERT INTO posts (content, username)
                    VALUES (?, ?)"""
            cursor = cursor.execute(sql, (new_post, current_user))
            conn.commit()
            sql1 = """SELECT id, content, username, created_at, follower_name
                  FROM posts
                  INNER JOIN followers ON username=followed_name
                  WHERE follower_name=?
                  UNION ALL
                  SELECT id, content, username, created_at, 'blank' AS follower_name
                  FROM posts
                  WHERE username=?
                  ORDER BY id DESC"""
            cursor.execute(sql1, (current_user, current_user))
            list2.clear()
            for row in cursor.fetchall():
                list2.append(row)
            current_page = current_user
            return render_template('frontpage.html', user=current_user, postlist = list2)
        elif request.form.get("searchuser") is not None:
            current_search = request.form['searchuser']
            sql1 = """SELECT * FROM posts WHERE username=? ORDER BY id DESC"""
            cursor.execute(sql1, (current_search,))
            list2.clear()
            for row in cursor.fetchall():
                list2.append(row)
            current_page = current_search
            print (current_page)
            return render_template('frontpage.html', user=current_search, postlist = list2)
        elif request.form.get("frienduser") is not None:
            friend_status = 0
            sql2 = """INSERT INTO followers (follower_name, followed_name, status)
                     VALUES (?, ?, ?)"""
            cursor = cursor.execute(sql2, (current_user, current_page, friend_status))
            conn.commit()
            sql1 = """SELECT * FROM posts WHERE username=? ORDER BY id DESC"""
            cursor.execute(sql1, (current_page,))
            list2.clear()
            for row in cursor.fetchall():
                list2.append(row)
            return render_template('frontpage.html', user=current_page, postlist = list2)
        elif request.form.get("friendlist") is not None:
            return redirect("/friends")
        elif request.form.get('sharebutton') is not None:
            sharedID = request.form.get('sharebutton')
            sql2 = """INSERT INTO shared_posts (shared_userid, post_id)
                     VALUES (?, ?)"""
            cursor.execute(sql2, (current_user, sharedID,))
            conn.commit()
            sql1 = """SELECT * FROM posts WHERE username=? ORDER BY id DESC"""
            cursor.execute(sql1, (current_page,))
            list2.clear()
            for row in cursor.fetchall():
                list2.append(row)
            return render_template('frontpage.html', user=current_page, postlist = list2)
    else:
        current_page = current_user
        return render_template('frontpage.html', user=current_user, postlist = list2)

@app.route('/friends', methods=['GET', 'POST'])
def friend():
    global current_user
    global current_page
    conn = db_connection()
    cursor = conn.cursor()
    sql3 = """SELECT * FROM followers WHERE followed_name=? AND status=0"""
    cursor.execute(sql3, (current_user,))
    list3 = []
    for row in cursor.fetchall():
                list3.append(row)
    if request.method == 'POST':
        if request.form.get('acceptbutton') is not None:
            friendid=request.form.get('acceptbutton')
            sql3= """UPDATE followers SET status=1 WHERE friendid=?"""
            cursor.execute(sql3, (friendid,))
            conn.commit()
        elif request.form.get('denybutton') is not None:
            friendid= request.form.get('denybutton')
            sql3= """DELETE FROM followers WHERE friendid=?"""
            cursor.execute(sql3, (friendid,))
            conn.commit()
    return render_template('friendlist.html', requestlist = list3)

"""
@app.route('/search', methods=['GET', 'POST'])       
def search():
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        new_search = request.form['username']
        sql = """"""
        cursor.execute(sql, (new_search,))
        test = cursor.fetchone()
        if not test:
            return render_template('search.html')
        elif test: 
            return render_template('mainpage.html')
    else:
        return render_template('search.html')
"""
if __name__ == "__main__":
    app.run(debug=True)

    
