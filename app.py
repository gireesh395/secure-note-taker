import os
import sqlite3
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = 'super_secret_spy_key'

DB_PATH = '/app/data/missions.db'

def init_db():
    if not os.path.exists('/app/data'):
        os.makedirs('/app/data')
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS missions 
                     (id TEXT PRIMARY KEY, content BLOB, secret_key TEXT)''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/drop', methods=['POST'])
def drop_mission():
    content = request.form.get('content')
    if not content: return redirect(url_for('index'))
    key = Fernet.generate_key()
    f = Fernet(key)
    enc_content = f.encrypt(content.encode())
    m_id = str(uuid.uuid4())[:8]
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('INSERT INTO missions VALUES (?, ?, ?)', (m_id, enc_content, key.decode()))
    return render_template('mission_success.html', mission_id=m_id)

@app.route('/retrieve', methods=['GET', 'POST'])
def retrieve():
    if request.method == 'POST':
        m_id = request.form.get('mission_id')
        with sqlite3.connect(DB_PATH) as conn:
            mission = conn.execute('SELECT * FROM missions WHERE id = ?', (m_id,)).fetchone()
            if mission:
                f = Fernet(mission[2].encode())
                decrypted = f.decrypt(mission[1]).decode()
                conn.execute('DELETE FROM missions WHERE id = ?', (m_id,))
                return render_template('view_mission.html', note=decrypted)
    return render_template('retrieve.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
