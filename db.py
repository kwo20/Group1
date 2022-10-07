import sqlite3

conn = sqlite3.connect("bickerdb.sqlite")

cursor = conn.cursor()
sql = """UPDATE posts
         SET created_at = null WHERE id = 12"""
            
cursor = cursor.execute(sql)
conn.commit()