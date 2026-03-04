from flask import Flask, request, render_template_string
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

# In a real SOC audit, this key would be a 'Secret' in AWS
# For now, we generate one for this session
key = Fernet.generate_key()
cipher_suite = Fernet(key)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Sangam Cyber Vault</title></head>
<body>
    <h1>🔒 Sangam Cyber Secure Vault</h1>
    <form method="POST">
        <textarea name="note" rows="4" cols="50" placeholder="Enter your secret note..."></textarea><br>
        <input type="submit" value="Encrypt & Save">
    </form>
    <hr>
    <h3>Last Action Status: {{ status }}</h3>
    {% if encrypted_note %}
        <p><strong>Encrypted Data (What hackers see):</strong><br> {{ encrypted_note }}</p>
    {% endif %}
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
            # The actual encryption happens here!
            encrypted_note = cipher_suite.encrypt(user_note.encode()).decode()
            status = "Note Encrypted and Secured!"
            
    return render_template_string(HTML_TEMPLATE, status=status, encrypted_note=encrypted_note)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
