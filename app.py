"""English -> French translation web app (Flask)."""
import os
import pickle

import numpy as np
from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

MAX_LENGTH = 23  # same padding length used during training

# ---------- Load model + tokenizers once at startup ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")

model = load_model(os.path.join(MODEL_DIR, "translator.keras"))

with open(os.path.join(MODEL_DIR, "english_tokenizer.pkl"), "rb") as f:
    english_tokenizer = pickle.load(f)
with open(os.path.join(MODEL_DIR, "french_tokenizer.pkl"), "rb") as f:
    french_tokenizer = pickle.load(f)

index_to_french = {i: w for w, i in french_tokenizer.word_index.items()}
index_to_french[0] = ""

app = Flask(__name__)


def translate(sentence: str) -> str:
    seq = english_tokenizer.texts_to_sequences([sentence.lower()])
    seq = pad_sequences(seq, maxlen=MAX_LENGTH, padding="post")
    prediction = model.predict(seq, verbose=0)[0]
    words = [index_to_french[int(np.argmax(p))] for p in prediction]
    return " ".join(w for w in words if w)


@app.route("/", methods=["GET", "POST"])
def home():
    sentence, translation, unknown, error = "", None, [], None
    if request.method == "POST":
        sentence = request.form.get("sentence", "").strip()
        if not sentence:
            error = "Please type a sentence."
        else:
            # words the model has never seen (they get skipped)
            unknown = [w for w in sentence.lower().split()
                       if not english_tokenizer.texts_to_sequences([w])[0]]
            translation = translate(sentence)
            if not translation:
                error = "None of these words are in the training vocabulary."
                translation = None
    return render_template("index.html", sentence=sentence,
                           translation=translation, unknown=unknown, error=error)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)), debug=False)
