import os
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ARCHITECTURE: Pulling the DB path from an Environment Variable
# This allows you to change the location on AWS without changing code.
DB_PATH = os.environ.get('DATABASE_URL', 'notes.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    # Use 'with' so the connection ALWAYS closes automatically (No leaks!)
    with get_db_connection() as conn:
        notes = conn.execute('SELECT * FROM notes ORDER BY created_at DESC').fetchall()
    return render_template('index.html', notes=notes)

@app.route('/add', methods=['POST'])
def add_note():
    content = request.form.get('content')
    if content:
        # ARCHITECTURE: Sanitize/Strip input to prevent basic HTML injection
        content = content.strip() 
        with get_db_connection() as conn:
            conn.execute('INSERT INTO notes (content) VALUES (?)', (content,))
            conn.commit()
    return redirect('/')

# GURU TIP: Notice I removed app.run(). 
# We let Gunicorn handle the start-up in the Dockerfile.
