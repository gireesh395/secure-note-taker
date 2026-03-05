from flask import Flask, request, render_template_string
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

# --- SECRETS MANAGEMENT ---
SECRET_KEY = os.getenv("SANGAM_VAULT_KEY")
if not SECRET_KEY:
    SECRET_KEY = Fernet.generate_key().decode()
cipher_suite = Fernet(SECRET_KEY.encode())

# --- PERSISTENCE CONFIG ---
DATA_DIR = "/app/data"
DATA_FILE = os.path.join(DATA_DIR, "notes.txt")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- PROFESSIONAL UI TEMPLATE ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sangam Cyber | Secure Vault Service</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; background-color: #f4f7f6; color: #333; }
        .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        textarea { width: 100%; border: 1px solid #ddd; padding: 15px; border-radius: 8px; font-size: 16px; margin-bottom: 10px; }
        .btn { background: #2c3e50; color: white; padding: 12px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; }
        .btn:hover { background: #34495e; }
        .note-card { background: #fff; border: 1px solid #eee; padding: 15px; margin-top: 15px; border-left: 5px solid #3498db; border-radius: 4px; }
        .encrypted { font-family: monospace; color: #7f8c8d; font-size: 12px; word-break: break-all; }
        .decrypted { color: #27ae60; font-weight: 500; margin-top: 5px; }
        .status { background: #d4edda; color: #155724; padding: 10px; border-radius: 6px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Sangam Cyber Secure Vault</h1>
        
        {% if status %}<div class="status">{{ status }}</div>{% endif %}

        <form method="POST">
            <textarea name="note" rows="3" placeholder="Enter a new secret to encrypt..."></textarea>
            <button type="submit" class="btn">Encrypt & Sync to Ubuntu Disk</button>
        </form>

        <hr style="margin: 40px 0;">
        
        <h2>🕵️‍♂️ Vault Explorer (Live Decryption)</h2>
        <p><small>Reading directly from <code>/home/ubuntu/sangam_data/notes.txt</code></small></p>
        
        {% for n in all_notes %}
            <div class="note-card">
                <div class="encrypted"><strong>Ciphertext:</strong> {{ n.encrypted }}</div>
                <div class="decrypted"><strong>Decrypted:</strong> {{ n.decrypted }}</div>
            </div>
        {% else %}
            <p>No notes found in the vault yet.</p>
        {% endfor %}
    </div>
</body>
</html>
'''

def fetch_and_decrypt():
    """Reads the persistent file and decrypts every line for the UI"""
    decoded_notes = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            for line in f:
                cipher = line.strip()
                if cipher:
                    try:
                        plain = cipher_suite.decrypt(cipher.encode()).decode()
                        decoded_notes.append({"encrypted": cipher, "decrypted": plain})
                    except:
                        decoded_notes.append({"encrypted": cipher, "decrypted": "[ERROR: WRONG KEY]"})
    return decoded_notes[::-1] # Show newest first

@app.route('/', methods=['GET', 'POST'])
def home():
    status = None
    if request.method == 'POST':
        note = request.form.get('note')
        if note:
            # 1. Encrypt
            cipher = cipher_suite.encrypt(note.encode()).decode()
            # 2. Force-Sync to Disk
            with open(DATA_FILE, "a") as f:
                f.write(cipher + "\n")
                f.flush()
                os.fsync(f.fileno())
            status = "🚀 Note successfully synced to persistent storage!"
    
    # 3. Always fetch the latest notes for the UI
    notes = fetch_and_decrypt()
    return render_template_string(HTML_TEMPLATE, status=status, all_notes=notes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
