from flask import Flask, url_for, request
import json
import sqlite3
from app import app
#test_client = app.test_client()
#response = app.test_client().get("/login", follow_redirects=True)

def test_comment():
  conn = sqlite3.connect("bickerdb.sqlite")
  cursor = conn.cursor()
### going to home page
  test_client = app.test_client()
  response = test_client.get('/', follow_redirects=True)
  login_post = test_client.post('/login', data=dict(username='ecology', password='test'))
  html = login_post.data.decode()
  assert "/frontpage" in html
  response2 = test_client.get('/frontpage', follow_redirects=True)

### testing creating comment
  commentbutton = test_client.post('/frontpage', data=dict(comment_button='test comment here', commentbutton="9"))
  cursor.execute("SELECT * FROM comments WHERE comment_content = 'test comment here'")
  post_list = []
  for row in cursor.fetchall():
        post_list.append(row)
  test = False
  if post_list is not None:
    test = True
  assert test == True
  cursor.execute("DELETE FROM comments WHERE comment_content = 'test comment here'")
  conn.commit()
  assert response2.request.path == '/frontpage'
  assert response.status_code == 200




def test_like():
  conn = sqlite3.connect("bickerdb.sqlite")
  cursor = conn.cursor()
### goes to front page
  test_client = app.test_client()
  response = test_client.get('/', follow_redirects=True)
  login_post = test_client.post('/login', data=dict(username='ecology', password='test'))
  html = login_post.data.decode()
  assert "/frontpage" in html
  response2 = test_client.get('/frontpage', follow_redirects=True)

### creates a post 
  fake_post = test_client.post('/frontpage', data=dict(post_input='test post here', postsubmit=""))

### tests like button
  likebutton = test_client.post('/frontpage', data=dict(likebutton=""))
  cursor.execute("SELECT likes FROM posts WHERE id == 1")

  assert response.status_code == 200
  cursor.execute("DELETE FROM posts WHERE content = 'test post here'")

  conn.commit()

  assert response2.request.path == '/frontpage'
  assert response.status_code == 200


def test_share():

    conn = sqlite3.connect("bickerdb.sqlite")
    cursor = conn.cursor()
    ### goes to front page
    test_client = app.test_client()
    response = test_client.get('/', follow_redirects=True)
    login_post = test_client.post('/login', data=dict(username='ecology', password='test'))
    html = login_post.data.decode()
    assert "/frontpage" in html

    test_client.get('/frontpage', follow_redirects=True)
    searchbutton = test_client.post('/frontpage', data=dict(searchuser='admin1', searchbutton=""))
    html2 = searchbutton.data.decode()
    assert "admin1" in html2
### pressing share button
    test_client.post('/frontpage', data=dict(sharebutton="13"))

###checking database to see if post was shared
    cursor.execute("SELECT * FROM shared_posts WHERE shared_userid='ecology' AND post_id=13""")
    post_list = []
    for row in cursor.fetchall():
        post_list.append(row)
    test = False
    if post_list is not None:
      test = True
    assert test == True

    cursor.execute("DELETE FROM shared_posts WHERE shared_userid='ecology' AND post_id=13")
    conn.commit()
