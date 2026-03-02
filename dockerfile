# 1. Use a tiny version of Python as our base
FROM python:3.9-slim

# 2. Set the "Home Folder" inside the box
WORKDIR /app

# 3. Copy our "Shopping List" into the box
COPY requirements.txt .

# 4. Tell the box to install the ingredients
RUN pip install -r requirements.txt

# 5. Copy our "Recipe" (app.py) into the box
COPY app.py .

# 6. Start the app when the box opens
CMD ["python", "app.py"]
