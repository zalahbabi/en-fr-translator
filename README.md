# English → French Neural Machine Translation — Flask + Docker + Google Cloud Run

A web app that translates simple English sentences to French using a sequence-to-sequence
Bidirectional GRU model built with TensorFlow/Keras, served with Flask, containerized with
Docker, and deployed on Google Cloud Run.

**Live demo:** https://en-fr-translator-297513110687.us-central1.run.app
*(first request after idle takes ~30–60 s while the container wakes up)*

**Repository:** https://github.com/zalahbabi/en-fr-translator

## Model

Trained on the ZAKA AI EN/FR parallel corpus (137,860 aligned sentence pairs; small
vocabulary of ~227 English / ~354 French words covering weather, months, fruits, animals).

Architecture:

```
Embedding (256) → Bidirectional GRU (256) → RepeatVector (23)
→ Bidirectional GRU (256, return_sequences) → TimeDistributed Dense (softmax)
```

Trained 10 epochs, sparse categorical cross-entropy, Adam — **~95% validation accuracy**.
Input and output sentences are padded to 23 tokens. Words outside the training vocabulary
are skipped and flagged to the user in the UI.

## Project structure

```
.
├── app.py                  # Flask app: loads model + tokenizers, serves UI and /health
├── templates/
│   └── index.html          # Web interface
├── model/
│   ├── translator.keras    # Trained seq2seq model
│   ├── english_tokenizer.pkl
│   └── french_tokenizer.pkl
├── requirements.txt
├── Dockerfile
└── save_for_deployment.py  # Run in the training notebook to export model/ files
```

## Run locally

```bash
pip install -r requirements.txt
python app.py
# open http://localhost:7860
```

## Run with Docker

```bash
docker build -t en-fr-translator .
docker run -p 7860:7860 en-fr-translator
# open http://localhost:7860
```

Note for Apple Silicon: `tensorflow-cpu` has no Linux arm64 wheels. To build locally on
an M-series Mac, either swap `tensorflow-cpu` for `tensorflow` in requirements.txt, or
build with `docker build --platform linux/amd64 ...`. Cloud builds (x86_64) are unaffected.

## Deploy to Google Cloud Run

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
gcloud run deploy en-fr-translator \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300
```

Cloud Build builds the Dockerfile remotely and prints the public Service URL when done.
The Dockerfile binds gunicorn to `$PORT`, which Cloud Run injects automatically.

## API

- `GET /` — web UI
- `POST /` — form field `sentence`, returns the rendered translation
- `GET /health` — returns `{"status": "ok"}` (liveness check)

## Known limitations

- Vocabulary is limited to the training corpus (~227 English words); unknown words are skipped.
- Rare sentence patterns (e.g. animal sentences) may borrow phrasing from more frequent
  patterns in the training data.
- Improvements: attention mechanism, more epochs, BLEU evaluation, Transformer architecture.
