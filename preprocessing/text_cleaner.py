import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ---------------- SAFE NLTK LOAD (NO DOWNLOADS) ----------------

def load_stopwords():
    try:
        return set(stopwords.words("english"))
    except LookupError:
        return set()

def safe_tokenize(text):
    try:
        return word_tokenize(text)
    except LookupError:
        return text.split()

stop_words = load_stopwords()
lemmatizer = WordNetLemmatizer()

GENDER_WORDS = {"male", "female", "he", "she", "his", "her"}

# ---------------- CLEANING FUNCTIONS ----------------

def remove_bias(text: str) -> str:
    if not text:
        return ""

    # Remove email
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove phone numbers
    text = re.sub(r"\b\d{10}\b", " ", text)

    # Remove gender words
    for word in GENDER_WORDS:
        text = re.sub(rf"\b{word}\b", " ", text, flags=re.IGNORECASE)

    return text


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = remove_bias(text)
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)

    tokens = safe_tokenize(text)

    cleaned_tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(cleaned_tokens)
