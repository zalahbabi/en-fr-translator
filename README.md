# EN → FR Translator — Flask + Docker Deployment

Deployment of the Week 8 machine translation model (Embedding + Bidirectional GRU seq2seq).

## Project structure

```
translator-deployment/
├── app.py                  # Flask app
├── templates/
│   └── index.html          # Web UI
├── model/                  # ← YOU add these (from save_for_deployment.py)
│   ├── translator.keras
│   ├── english_tokenizer.pkl
│   └── french_tokenizer.pkl
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── save_for_deployment.py  # Run in the Colab notebook, not in Docker
```

## Step 1 — Export the model from Colab

1. Open `Week_8.ipynb`, run all cells through training.
2. Paste the contents of `save_for_deployment.py` in a new cell and run it. It downloads `model.zip`.
3. Note the printed TensorFlow version and update `tensorflow-cpu==...` in `requirements.txt` to match.
4. Unzip `model.zip` and place the `model/` folder inside this project as shown above.

## Step 2 — Run locally (no Docker, quick test)

```bash
cd translator-deployment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:7860

## Step 3 — Run with Docker

```bash
docker build -t en-fr-translator .
docker run -p 7860:7860 en-fr-translator
```

Open http://localhost:7860

## Step 4 — Deploy online

### Option A: Hugging Face Spaces (recommended, free, Docker-native)

1. Create a Space at https://huggingface.co/new-space → SDK: **Docker** → Blank.
2. Push this whole folder (including `model/`) to the Space repo:

```bash
git clone https://huggingface.co/spaces/<your-username>/<space-name>
cp -r translator-deployment/* <space-name>/
cd <space-name>
git add .
git commit -m "Deploy EN-FR translator"
git push
```

3. If the model file is >10 MB, track it with Git LFS first:

```bash
git lfs install
git lfs track "*.keras" "*.pkl"
git add .gitattributes
```

The Space builds the Dockerfile automatically and serves on port 7860.
Your public link: `https://huggingface.co/spaces/<your-username>/<space-name>`

### Option B: Render

1. Push the project to a GitHub repo (use Git LFS for the model if >100 MB).
2. On https://render.com → New → Web Service → connect the repo.
3. Runtime: **Docker**. Render injects `$PORT` automatically — the Dockerfile handles it.
4. Free instance works but cold-starts; first request may take ~1 min.

## Notes / troubleshooting

- **Model fails to load**: the TF version in `requirements.txt` must match the Colab training version (printed by `save_for_deployment.py`).
- **Out of memory on free tiers**: `tensorflow-cpu` + 1 gunicorn worker keeps RAM low; the model itself is small.
- **Health check**: `GET /health` returns `{"status": "ok"}` — useful for Render health checks.
# en-fr-translator
