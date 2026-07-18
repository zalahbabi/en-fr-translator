FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code, templates, and model files
COPY . .

# Hugging Face Spaces expects port 7860; Render/Railway inject $PORT
ENV PORT=7860
EXPOSE 7860

CMD gunicorn --bind 0.0.0.0:${PORT} --workers 1 --timeout 120 app:app
