from utils.skills import SKILLS_DB


def extract_skills(cleaned_text):
    extracted = []

    for skill in SKILLS_DB:
        if skill in cleaned_text:
            extracted.append(skill)

    return list(set(extracted))


if __name__ == "__main__":
    sample_text = "python sql machine learning flask docker aws"
    print("Extracted Skills:", extract_skills(sample_text))
