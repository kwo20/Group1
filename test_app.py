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
    create_post = test_client.post('/create', data=dict(username='test_account', password='test_password'))
    html = create_post.data.decode()
    assert "/login" in html
    assert response.status_code == 200
    cursor.execute("DELETE FROM users WHERE username = 'test_account'")
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


    #username = 'ecology'
    #password = 'test'
    #test_client.post('/login', data=dict(test_user='ecology', test_pass='test'))
    #assert response.request.path == "/frontpage"
    
