import os
from models.matcher import match_resume_with_jd


def optimize_roles(resume_text, jd_folder="data/job_descriptions"):
    role_scores = {}

    for jd_file in os.listdir(jd_folder):
        if jd_file.endswith(".txt"):
            role_name = jd_file.replace(".txt", "").replace("_", " ").title()

            with open(os.path.join(jd_folder, jd_file), "r", encoding="utf-8") as f:
                jd_text = f.read()

            score = match_resume_with_jd(resume_text, jd_text)
            role_scores[role_name] = score

    # Best fit role
    best_role = max(role_scores, key=role_scores.get)

    return role_scores, best_role


if __name__ == "__main__":
    sample_resume = "python sql data analysis visualization statistics"
    scores, best = optimize_roles(sample_resume)
    print(scores)
    print("Best Role:", best)
