# 1. Use a tiny version of Python
FROM python:3.9-slim

# 2. Set the "Home Folder" inside the box
WORKDIR /app

# 3. Copy the "Shopping List" first (for faster builds)
COPY requirements.txt .

# 4. Install the ingredients
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the Brain (app.py) and the Face (templates folder)
COPY app.py .
COPY templates/ ./templates/

# 6. Start the app
CMD ["python", "app.py"]
