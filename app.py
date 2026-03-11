import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 🏛️ Database Architecture: Storing the 'Encrypted Mission'
# Path is /app/data/missions.db to match your Docker Volume
db_path = os.path.join('/app/data', 'missions.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db = SQLAlchemy(app)

class Mission(db.Model):
    id = db.Column(db.String(8), primary_key=True) # The 'Spy Code'
    ciphertext = db.Column(db.LargeBinary, nullable=False)
    salt = db.Column(db.LargeBinary, nullable=False) # For secure key derivation

# 🛠️ HELPER: Turn a 'Human Password' into a 'Secure Key'
def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

@app.route('/')
def index():
    return render_template('index.html') # The 'Handler' screen

@app.route('/drop', methods=['POST'])
def drop_mission():
    mission_text = request.form.get('mission_text')
    passphrase = request.form.get('passphrase') # The secret key known by agent
    
    if not mission_text or not passphrase:
        return "Missing data", 400

    # 1. Generate unique 8-char Spy ID
    m_id = str(uuid.uuid4())[:8].upper()
    
    # 2. Encrypt mission
    salt = os.urandom(16)
    key = derive_key(passphrase, salt)
    f = Fernet(key)
    encrypted_data = f.encrypt(mission_text.encode())

    # 3. Save to DB
    new_mission = Mission(id=m_id, ciphertext=encrypted_data, salt=salt)
    db.session.add(new_mission)
    db.session.commit()

    return render_template('mission_success.html', m_id=m_id)

@app.route('/retrieve', methods=['GET', 'POST'])
def retrieve_mission():
    if request.method == 'POST':
        m_id = request.form.get('m_id').upper()
        passphrase = request.form.get('passphrase')
        
        mission = Mission.query.filter_by(id=m_id).first()
        
        if mission:
            try:
                # 1. Re-derive key
                key = derive_key(passphrase, mission.salt)
                f = Fernet(key)
                decrypted_text = f.decrypt(mission.ciphertext).decode()

                # 🏛️ THE SHREDDER: Delete from DB immediately after reading
                db.session.delete(mission)
                db.session.commit()

                return render_template('view_mission.html', content=decrypted_text)
            except:
                flash("Invalid Cipher Key. Mission compromised?")
        else:
            flash("Mission ID not found.")
            
    return render_template('retrieve.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
