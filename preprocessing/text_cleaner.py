import re
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ---------------- NLTK SAFE DOWNLOAD (FOR DEPLOYMENT) ----------------
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")

# ---------------- INITIALIZATION ----------------
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

GENDER_WORDS = ["male", "female", "he", "she", "his", "her"]


# ---------------- BIAS REMOVAL ----------------
def remove_bias(text):
    if not text:
        return ""

    # Remove email
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove phone numbers
    text = re.sub(r"\b\d{10}\b", " ", text)

    # Remove gender-related words
    for word in GENDER_WORDS:
        text = re.sub(rf"\b{word}\b", " ", text, flags=re.IGNORECASE)

    return text


# ---------------- MAIN CLEANING FUNCTION ----------------
def clean_text(text):
    if not text:
        return ""

    # 1. Bias removal
    text = remove_bias(text)

    # 2. Lowercase
    text = text.lower()

    # 3. Remove special characters & numbers
    text = re.sub(r"[^a-z\s]", " ", text)

    # 4. Tokenization
    tokens = word_tokenize(text)

    # 5. Stopword removal + lemmatization
    tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(tokens)
