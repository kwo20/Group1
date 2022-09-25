from flask import Flask, render_template, redirect, url_for, request, jsonify
import json
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('frontpage.html')

if __name__ == "__main__":
    app.run(debug=True)