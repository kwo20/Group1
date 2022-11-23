from flask import Flask, url_for, request
import json
import sqlite3
from app import app
#test_client = app.test_client()
#response = app.test_client().get("/login", follow_redirects=True)
def test_index_route():
    test_client = app.test_client()
    response = test_client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'

def test_create_account():
    conn = sqlite3.connect("bickerdb.sqlite")
    cursor = conn.cursor()
    
    test_client = app.test_client()
    response = test_client.get('/create', follow_redirects=True)
    create_post = test_client.post('/create', data=dict(username='testaccount', password='testpassword'))
    html = create_post.data.decode()
    assert '/login' in html
    assert response.status_code == 200
    cursor.execute("DELETE FROM users WHERE username = 'testaccount'")
    conn.commit()

def test_login():
    test_client = app.test_client()
    response = test_client.get('/', follow_redirects=True)
    login_post = test_client.post('/login', data=dict(username='ecology', password='test'))
    html = login_post.data.decode()
    assert "/frontpage" in html
    assert response.status_code == 200

def test_login_bypass():
    test_client = app.test_client()
    response = test_client.get('/frontpage', follow_redirects=True)
    assert response.request.path is not '/frontpage'
    assert response.status_code == 200

def test_friendpage():
    test_client = app.test_client()
    response = test_client.get('/', follow_redirects=True)
    login_post = test_client.post('/login', data=dict(username='ecology', password='test'))
    html = login_post.data.decode()
    assert "/frontpage" in html
    response2 = test_client.get('/friends', follow_redirects=True)
    assert response2.request.path == "/friends"
    response2.status_code == 200

def test_friendsbutton():
    test_client = app.test_client()
    response = test_client.get('/', follow_redirects=True)
    login_post = test_client.post('/login', data=dict(username='ecology', password='test'))

    response2 = test_client.get('/frontpage', follow_redirects=True)
    html = response2.data.decode()

    assert 'Friend ecology' in html
    assert response.status_code == 200
    assert response2.status_code == 200

def test_friendsfunction():
    conn = sqlite3.connect("bickerdb.sqlite")
    cursor = conn.cursor()

    test_client = app.test_client()
    response = test_client.get('/', follow_redirects=True)
    login_post = test_client.post('/login', data=dict(username='ecology', password='test'))
    html = login_post.data.decode()

    assert "/frontpage" in html

    response2 = test_client.get('/frontpage', follow_redirects=True)
    diffacc = test_client.post('/frontpage', data=dict(searchuser='admin', searchbutton=""))
    friendbuttontest = test_client.post('/frontpage', data=dict(friendbutton=""))

    friendbuttontest = test_client.get('/friends', follow_redirects=True)
    html2 = friendbuttontest.data.decode()

    assert friendbuttontest.request.path == "/friends"
    assert "admin" in html2

    friendbuttontest.status_code == 200

def test_create_post():
    conn = sqlite3.connect("bickerdb.sqlite")
    cursor = conn.cursor()

    test_client = app.test_client()
    test_client.get('/', follow_redirects=True)
    test_client.post('/login', data=dict(username='ecology', password='test'))
    test_client.get('/frontpage', follow_redirects=True)
    friend_list = test_client.post('/frontpage', data=dict(post_input='test post here', postsubmit=""))
    html2 = friend_list.data.decode()
    assert "test post here" in html2
    cursor.execute("DELETE FROM posts WHERE content = 'test post here'")
    conn.commit()

def test_like_post():
    conn = sqlite3.connect("bickerdb.sqlite")
    cursor = conn.cursor()
    test_client = app.test_client()
    test_client.get('/', follow_redirects=True)
    test_client.post('/login', data=dict(username='ecology', password='test'))
    cursor.execute("SELECT likes FROM posts WHERE id=9""")
    original_likecount = cursor.fetchone()
    test_client.get('/frontpage', follow_redirects=True)
    test_client.post('/frontpage', data=dict(likebutton="9"))
    cursor.execute("SELECT likes FROM posts WHERE id=9""")
    original_likecount2 = cursor.fetchone()
    assert original_likecount2 > original_likecount
    cursor.execute("""UPDATE posts SET likes = likes - 1 WHERE id=9""")
    conn.commit()

def test_comment_post():
    conn = sqlite3.connect("bickerdb.sqlite")
    cursor = conn.cursor()
    test_client = app.test_client()
    test_client.get('/', follow_redirects=True)
    test_client.post('/login', data=dict(username='ecology', password='test'))
    test_client.get('/frontpage', follow_redirects=True)
    test_client.post('/frontpage', data=dict(comment_button='This is a test comment.', commentbutton="23"))
    cursor.execute("SELECT * FROM comments WHERE comment_content = 'This is a test comment.'")
    testlist = []
    for row in cursor.fetchall():
        testlist.append(row)
    comment_exists = False
    if testlist is not None:
      comment_exists = True
    assert comment_exists == True

    cursor.execute("DELETE FROM comments WHERE comment_content = 'This is a test comment.'")
    conn.commit()

    #username = 'ecology'
    #password = 'test'
    #test_client.post('/login', data=dict(test_user='ecology', test_pass='test'))
    #assert response.request.path == "/frontpage"
