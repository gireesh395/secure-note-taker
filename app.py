from flask import Flask, request, render_template_string
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

# --- INFRASTRUCTURE MECHANIC 1: ENVIRONMENT SECRETS ---
# A DevOps Engineer never hardcodes keys. We pull it from the OS environment.
# On your Ubuntu server, we will set SANGAM_VAULT_KEY later.
SECRET_KEY = os.getenv("SANGAM_VAULT_KEY")

if not SECRET_KEY:
    # Fallback for development/testing so the app doesn't crash on your VM
    # In a SOC Audit, you'd configure this to throw an error instead.
    SECRET_KEY = Fernet.generate_key().decode()

cipher_suite = Fernet(SECRET_KEY.encode())

# --- INFRASTRUCTURE MECHANIC 2: PERSISTENT STORAGE ---
# This is the "Internal Room" path.
# We will "Mount" this to /home/ubuntu/sangam_data on the real server.
DATA_DIR = "/app/data"
DATA_FILE = os.path.join(DATA_DIR, "notes.txt")

# Create the folder inside the container if it doesn't exist
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
        <p><strong>DevOps Audit:</strong> Persistence & Environment Secrets</p>
        
        <form method="POST">
            <textarea name="note" rows="5" placeholder="Type a secret note here... It will be encrypted and saved to the Ubuntu hard drive."></textarea>
            <input type="submit" value="Encrypt & Save to Permanent Storage">
        </form>

        {% if status %}
            <div class="status"><strong>Status:</strong> {{ status }}</div>
        {% endif %}

        {% if encrypted_note %}
            <div class="encrypted-box">
                <strong>AES-Encrypted Result:</strong><br><br>
                {{ encrypted_note }}
            </div>
            <p><small>Check /home/ubuntu/sangam_data/notes.txt on your server to see it saved!</small></p>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    status = "Waiting for input..."
    encrypted_note = None
    
    if request.method == 'POST':
        user_note = request.form.get('note')
        if user_note:
            # 1. Logic: Encrypt the note
            encrypted_note = cipher_suite.encrypt(user_note.encode()).decode()
            
            # 2. Infrastructure: Save to the "Mounted Portal"
            try:
                with open(DATA_FILE, "a") as f:
                    f.write(encrypted_note + "\n")
                status = "Success! Note encrypted and saved to persistent disk."
            except Exception as e:
                status = f"Infrastructure Error: {str(e)}"
            
    return render_template_string(HTML_TEMPLATE, status=status, encrypted_note=encrypted_note)

if __name__ == '__main__':
    # Standard Flask port
    app.run(host='0.0.0.0', port=5000)
