from flask import Flask, request, render_template_string
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

# --- INFRASTRUCTURE MECHANIC 1: ENVIRONMENT SECRETS ---
# The app looks in the server's RAM for the key.
SECRET_KEY = os.getenv("SANGAM_VAULT_KEY")

if not SECRET_KEY:
    # Fallback so the app doesn't crash during development on your Debian VM.
    SECRET_KEY = Fernet.generate_key().decode()

cipher_suite = Fernet(SECRET_KEY.encode())

# --- INFRASTRUCTURE MECHANIC 2: PERSISTENT STORAGE ---
# This is the path INSIDE the container that we mount to /home/ubuntu/sangam_data.
DATA_DIR = "/app/data"
DATA_FILE = os.path.join(DATA_DIR, "notes.txt")

# Ensure the directory exists inside the "VR world" (the container)
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- FRONTEND UI ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sangam Cyber Vault</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f0f2f5; }
        .container { max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: #1a2a3a; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }
        textarea { width: 100%; border: 1px solid #ddd; padding: 15px; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        input[type="submit"] { background: #2c3e50; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; margin-top: 15px; width: 100%; font-weight: bold; }
        input[type="submit"]:hover { background: #34495e; }
        .status { color: #27ae60; background: #e8f5e9; padding: 10px; border-radius: 6px; margin-top: 20px; }
        .encrypted-box { margin-top: 20px; word-break: break-all; background: #222; color: #00ff00; padding: 15px; border-radius: 6px; font-family: monospace; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Sangam Cyber Vault</h1>
        <p><strong>Infrastructure Status:</strong> Persistence & Force-Sync Active</p>
        
        <form method="POST">
            <textarea name="note" rows="5" placeholder="Type your secret note... It will be force-synced to the Ubuntu disk."></textarea>
            <input type="submit" value="Encrypt & Save to Permanent Storage">
        </form>

        {% if status %}
            <div class="status"><strong>System Log:</strong> {{ status }}</div>
        {% endif %}

        {% if encrypted_note %}
            <div class="encrypted-box">
                <strong>Encrypted Data:</strong><br><br>
                {{ encrypted_note }}
            </div>
            <p><small>Check /home/ubuntu/sangam_data/notes.txt on your server!</small></p>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    status = "System Ready. Waiting for input..."
    encrypted_note = None
    
    if request.method == 'POST':
        user_note = request.form.get('note')
        if user_note:
            # 1. Logic: Encrypt the note
            encrypted_note = cipher_suite.encrypt(user_note.encode()).decode()
            
            # 2. INFRASTRUCTURE MECHANIC: The "Force-Sync" Write
            try:
                # Open for appending ('a') with UTF-8 encoding
                with open(DATA_FILE, "a", encoding="utf-8") as f:
                    f.write(encrypted_note + "\n")
                    f.flush()            # Force data out of Python's memory buffer
                    os.fsync(f.fileno()) # Force the OS to write to the physical hard drive
                status = "Success! Note encrypted and force-synced to persistent disk."
            except Exception as e:
                status = f"Infrastructure Write Error: {str(e)}"
            
    return render_template_string(HTML_TEMPLATE, status=status, encrypted_note=encrypted_note)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
