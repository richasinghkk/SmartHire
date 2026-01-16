from sklearn.feature_extraction.text import TfidfVectorizer


def explain_match(resume_text, jd_text, top_n=10):
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform([resume_text, jd_text])

    feature_names = vectorizer.get_feature_names_out()

    resume_vector = tfidf[0].toarray()[0]
    jd_vector = tfidf[1].toarray()[0]

    matched = []
    missing = []

    for i, word in enumerate(feature_names):
        if jd_vector[i] > 0:
            if resume_vector[i] > 0:
                matched.append(word)
            else:
                missing.append(word)

    return matched[:top_n], missing[:top_n]
