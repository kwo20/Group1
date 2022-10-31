from flask import Flask, render_template, redirect, url_for, request, jsonify
import json
import sqlite3
import random
current_user = None
current_page = None
app = Flask(__name__)
#Connect to database
def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("bickerdb.sqlite")
    except sqlite3.error as e:
        print(e)
    return conn

#Defaults to login page
@app.route('/')
def index():
    return redirect("/login")

#Page for creating an account
@app.route('/create', methods=['GET', 'POST'])
def create_account():
    conn = db_connection()
    cursor = conn.cursor()
    #Upon information submit, insert into database and redirect to login
    if request.method == 'POST':
        account_username = request.form['username']
        account_password = request.form['password']
        sql_query = """INSERT INTO users (username, password)
                 VALUES (?, ?)"""
        cursor = cursor.execute(sql_query, (account_username, account_password))
        conn.commit()
        return redirect("/login")
    else:
        return render_template('create.html')

#Page for logging into Bicker
@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = db_connection()
    cursor = conn.cursor()
    #Checks information against database, redirects to frontpage if correct.
    if request.method == 'POST':
        cursor.execute("""SELECT password FROM users WHERE username=?""", (request.form['username'],))
        login_info = cursor.fetchone()
        if not login_info:
            return render_template('login.html')
        elif login_info[0] == request.form['password']:
            global current_user
            current_user = request.form['username']
            return redirect('/frontpage')
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')

#Frontpage of Bicker
@app.route('/frontpage', methods=['GET', 'POST'])
def frontpage():
    global current_user
    global current_page
    #Check for URL bypassing
    if current_user is None:
        return redirect("/login")
    conn = db_connection()
    cursor = conn.cursor()
    #Obtains all posts, shared post, and followed posts
    cursor.execute("""SELECT id, content, username, created_at, likes, follower_name
                  FROM posts
                  INNER JOIN followers ON username=followed_name
                  WHERE follower_name=?
                  UNION ALL
                  SELECT id, content, username, created_at, likes, 'blank' AS follower_name
                  FROM posts
                  WHERE username=?
                  UNION ALL
                  SELECT id, content, username, created_at, likes, 'blank' AS follower_name
                  FROM posts
                  INNER JOIN shared_posts ON id=post_id
                  WHERE shared_userid=?
                  ORDER BY id DESC""", (current_user, current_user, current_user))
    post_list = []
    for row in cursor.fetchall():
            post_list.append(row)
    #If no posts, get empty post
    if not post_list:
        cursor.execute("""SELECT * FROM posts WHERE id=12""")
        for row in cursor.fetchall():
            post_list.append(row)

    #Get a list of all comments
    cursor.execute("""SELECT * FROM comments
                    ORDER BY comment_id ASC""")
    comment_list = []
    for row in cursor.fetchall():
            comment_list.append(row)
            
    if request.method == 'POST':
        #If post submit, puts post into database
        if request.form.get("post-input") is not None:
            new_post = request.form['post-input']
            sql_query = """INSERT INTO posts (content, username)
                    VALUES (?, ?)"""
            cursor = cursor.execute(sql_query, (new_post, current_user))
            conn.commit()
            sql_query = """SELECT id, content, username, created_at, likes, follower_name
                  FROM posts
                  INNER JOIN followers ON username=followed_name
                  WHERE follower_name=?
                  UNION ALL
                  SELECT id, content, username, created_at, likes, 'blank' AS follower_name
                  FROM posts
                  WHERE username=?
                  UNION ALL
                  SELECT id, content, username, created_at, likes, 'blank' AS follower_name
                  FROM posts
                  INNER JOIN shared_posts ON id=post_id
                  WHERE shared_userid=?
                  ORDER BY id DESC"""
            cursor.execute(sql_query, (current_user, current_user, current_user))
            post_list.clear()
            for row in cursor.fetchall():
                post_list.append(row)
            current_page = current_user
            return render_template('frontpage.html', user=current_user, postlist = post_list, 
                                    currentuser=current_user, commentlist = comment_list)
        #Display searched user's frontpage
        elif request.form.get("searchuser") is not None:
            current_search = request.form['searchuser']
            sql_query = """SELECT * FROM posts WHERE username=? ORDER BY id DESC"""
            cursor.execute(sql_query, (current_search,))
            post_list.clear()
            for row in cursor.fetchall():
                post_list.append(row)
            current_page = current_search
            print (current_page)
            return render_template('frontpage.html', user=current_search, postlist = post_list,
                                    currentuser=current_user, commentlist = comment_list)
        #Sends a friend request to whichever user the current page is on
        elif request.form.get("frienduser") is not None:
            friend_status = 0
            sql_query = """INSERT INTO followers (follower_name, followed_name, status)
                     VALUES (?, ?, ?)"""
            cursor = cursor.execute(sql_query, (current_user, current_page, friend_status))
            conn.commit()
            sql_query = """SELECT * FROM posts WHERE username=? ORDER BY id DESC"""
            cursor.execute(sql_query, (current_page,))
            post_list.clear()
            for row in cursor.fetchall():
                post_list.append(row)
            return render_template('frontpage.html', user=current_page, postlist = post_list,
                                    currentuser=current_user, commentlist = comment_list)
        #Goes to friend list page
        elif request.form.get("friendlist") is not None:
            return redirect("/friends")
        #Adds the shared post into the database
        elif request.form.get('sharebutton') is not None:
            sharedID = request.form.get('sharebutton')
            sql_query = """INSERT INTO shared_posts (shared_userid, post_id)
                     VALUES (?, ?)"""
            cursor.execute(sql_query, (current_user, sharedID,))
            conn.commit()
            #FIX THIS LATER
            #Needs better query
            sql_query = """SELECT * FROM posts WHERE username=? ORDER BY id DESC"""
            cursor.execute(sql_query, (current_page,))
            post_list.clear()
            for row in cursor.fetchall():
                post_list.append(row)
            return render_template('frontpage.html', user=current_page, postlist = post_list, 
                                    currentuser=current_user, commentlist = comment_list)
        #Increments the like counter for the post by 1
        #Add check for already liked
        elif request.form.get('likebutton') is not None:
            likedID = request.form.get('likebutton')
            sql_query = """UPDATE posts SET likes = likes + 1 WHERE id = ?"""
            cursor.execute(sql_query, (likedID,))
            conn.commit()
            #Needs to stay on current page but update
            return redirect("/frontpage")
        #Returns to current logged in user's frontpage
        elif request.form.get('return') is not None:
            return redirect("/frontpage")
        elif request.form.get('commentbutton') is not None:
            #print (request.form.get('commentbutton'))
            #print (request.form.get('comment-button'))
            if request.form.get('comment-button') is None:
                return redirect("/frontpage")
            else:
                post_id = request.form.get('commentbutton')
                comment_content = request.form.get('comment-button')
                sql_query = """INSERT INTO comments (commenter_user, post_id, comment_content)
                            VALUES (?, ?, ?)"""
                cursor.execute(sql_query, (current_user, post_id, comment_content,))
                conn.commit()
                return redirect("/frontpage")
    else:
        current_page = current_user
        return render_template('frontpage.html', user=current_user, postlist = post_list, 
                                currentuser=current_user, commentlist = comment_list)

#Page for friend list and friend requests
@app.route('/friends', methods=['GET', 'POST'])
def friends_list():
    global current_user
    global current_page
    conn = db_connection()
    cursor = conn.cursor()
    #Select all friend requests from database
    sql_query = """SELECT * FROM followers WHERE followed_name=? AND status=0"""
    cursor.execute(sql_query, (current_user,))
    friend_requests = []
    for row in cursor.fetchall():
                friend_requests.append(row)
    #Select all friends from database
    sql_query = """SELECT * FROM followers WHERE followed_name=? AND status=1"""
    cursor.execute(sql_query, (current_user,))
    friend_list = []
    for row in cursor.fetchall():
                friend_list.append(row)
    #Checks for accept or deny and handles accordingly
    if request.method == 'POST':
        if request.form.get('acceptbutton') is not None:
            friend_id=request.form.get('acceptbutton')
            sql_query= """UPDATE followers SET status=1 WHERE friendid=?"""
            cursor.execute(sql_query, (friend_id,))
            conn.commit()
        elif request.form.get('denybutton') is not None:
            friend_id= request.form.get('denybutton')
            sql_query= """DELETE FROM followers WHERE friendid=?"""
            cursor.execute(sql_query, (friend_id,))
            conn.commit()
    return render_template('friendlist.html', requestlist = friend_requests, friendlist=friend_list)

if __name__ == "__main__":
    app.run(debug=True)

#FOR COMMENTS IN DATABASE MAKE POST ID COMMEN TIS ON, WHO POSTED, and POST CONTENT
#WHEN PUTTING COMMENTS IN USE IF STATEMENT IN HTML, MIGHT NEED FOR LOOP ASWELL

    
