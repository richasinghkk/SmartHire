import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# -------- SAFE NLTK SETUP (RENDER FIX) --------
try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")

lemmatizer = WordNetLemmatizer()

GENDER_WORDS = ["male", "female", "he", "she", "his", "her"]


def remove_bias(text):
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\b\d{10}\b", " ", text)

    for word in GENDER_WORDS:
        text = re.sub(rf"\b{word}\b", " ", text, flags=re.IGNORECASE)

    return text


def clean_text(text):
    text = remove_bias(text)
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)

    tokens = word_tokenize(text)

    tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(tokens)
