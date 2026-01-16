from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def match_resume_with_jd(resume_text, jd_text):
    documents = [resume_text, jd_text]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    return round(similarity_score * 100, 2)


if __name__ == "__main__":
    resume = "python sql machine learning data analysis"
    jd = "looking for data analyst with python and sql"

    print("Match Score:", match_resume_with_jd(resume, jd), "%")
