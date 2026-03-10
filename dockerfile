# 1. Use a specific version (3.9-slim is good)
FROM python:3.11-slim

# 2. Add a non-root user for security (The "Internship Winner" move)
RUN useradd -m appuser

# 3. Set the "Home Folder"
WORKDIR /home/appuser/app

# 4. Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 5. Copy the code and change ownership to our safe user
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser templates/ ./templates/

# 6. Switch to the safe user
USER appuser

# 7. Start with Gunicorn (The Production-Grade Way)
# -w 4 means 4 "Cooks" working at the same time
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
