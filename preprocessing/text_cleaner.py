import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

GENDER_WORDS = ["male", "female", "he", "she", "his", "her"]


def remove_bias(text):
    # Remove email
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove phone numbers
    text = re.sub(r"\b\d{10}\b", " ", text)

    # Remove gender words
    for word in GENDER_WORDS:
        text = re.sub(rf"\b{word}\b", " ", text, flags=re.IGNORECASE)

    return text


def clean_text(text):
    # Bias removal first
    text = remove_bias(text)

    # Lowercase
    text = text.lower()

    # Remove special characters & numbers
    text = re.sub(r"[^a-z\s]", " ", text)

    # Tokenize
    tokens = word_tokenize(text)

    # Stopword removal + lemmatization
    tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(tokens)
