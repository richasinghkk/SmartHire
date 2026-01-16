def classify_experience(resume_text):
    experience_keywords = ["year", "years", "experience", "worked", "company"]

    for word in experience_keywords:
        if word in resume_text:
            return "Experienced"

    return "Fresher"


if __name__ == "__main__":
    print(classify_experience("I have 3 years of experience in Python"))
    print(classify_experience("Final year student with internship"))
