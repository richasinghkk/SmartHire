import PyPDF2
import docx
import os

from preprocessing.text_cleaner import clean_text
from utils.helpers import extract_skills
from models.matcher import match_resume_with_jd
from models.explainer import explain_match
from models.classifier import classify_experience
from models.bias_audit import generate_bias_audit
from models.resume_advisor import generate_resume_advice
from models.role_optimizer import optimize_roles
from models.analytics import generate_recruiter_analytics

# 🔥 PHASE 2 STEP 1 (Visual Analytics)
from models.visualizer import (
    generate_skill_gap_chart,
    generate_role_distribution_chart,
    generate_score_distribution
)


def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
    return text


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def parse_resume(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")


if __name__ == "__main__":
    resume_folder = "data/resumes"
    jd_path = "data/job_descriptions/jd.txt"

    # Load primary Job Description
    with open(jd_path, "r", encoding="utf-8") as file:
        jd_text = file.read()

    results = []

    for resume_file in os.listdir(resume_folder):
        path = os.path.join(resume_folder, resume_file)

        # 1. Extract raw resume text
        raw_text = parse_resume(path)

        # 2. Bias Audit
        bias_audit = generate_bias_audit(raw_text)

        # 3. Clean resume text
        cleaned_text = clean_text(raw_text)

        # 4. Extract skills
        skills = extract_skills(cleaned_text)

        # 5. ML-based matching
        score = match_resume_with_jd(cleaned_text, jd_text)

        # 6. Explainable AI
        matched, missing = explain_match(cleaned_text, jd_text)

        # 7. Experience classification
        experience_level = classify_experience(cleaned_text)

        # 8. Resume Improvement Advisor
        advice = generate_resume_advice(missing, experience_level)

        # 9. Multi-Role Optimization
        role_scores, best_role = optimize_roles(cleaned_text)

        results.append({
            "resume": resume_file,
            "score": score,
            "experience": experience_level,
            "skills": skills,
            "matched": matched,
            "missing": missing,
            "advice": advice,
            "bias_audit": bias_audit,
            "role_scores": role_scores,
            "best_role": best_role
        })

    # 🔥 Rank resumes
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    # 🔥 Recruiter Analytics
    analytics = generate_recruiter_analytics(results)

    # 🔥 PHASE 2 STEP 1: Generate Charts
    os.makedirs("static/charts", exist_ok=True)

    generate_skill_gap_chart(
        analytics["top_missing_skills"],
        "static/charts/skill_gap.png"
    )

    generate_role_distribution_chart(
        analytics["role_distribution"],
        "static/charts/role_distribution.png"
    )

    scores = [r["score"] for r in results]
    generate_score_distribution(
        scores,
        "static/charts/score_distribution.png"
    )

    # ---------- CONSOLE OUTPUT ----------
    print("\n=========== RANKED RESUMES ===========\n")

    for idx, res in enumerate(results, start=1):
        print(f"Rank {idx}: {res['resume']}")
        print(f"Match Score: {res['score']}%")
        print(f"Experience Level: {res['experience']}")
        print(f"Extracted Skills: {res['skills']}")
        print(f"Matched Terms: {res['matched']}")
        print(f"Missing Terms: {res['missing']}")

        print("\nBias Audit Report:")
        for item in res["bias_audit"]:
            print("✔", item)

        print("\nAI Resume Improvement Advice:")
        for tip in res["advice"]:
            print("•", tip)

        print("\nRole Fit Analysis:")
        for role, s in res["role_scores"].items():
            print(f"• {role} → {s}%")
        print("Best Fit Role:", res["best_role"])

        print("-" * 65)

    print("\n=========== RECRUITER ANALYTICS DASHBOARD ===========\n")
    print("Total Resumes Screened:", analytics["total_resumes"])
    print("Average Match Score:", analytics["average_score"], "%")
    print("Strong Hire Candidates:", analytics["strong_hires"])

    print("\nTop Missing Skills:")
    for skill, count in analytics["top_missing_skills"]:
        print(f"• {skill} ({count})")

    print("\nBest Fit Role Distribution:")
    for role, count in analytics["role_distribution"].items():
        print(f"• {role}: {count}")
