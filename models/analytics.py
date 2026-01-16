from collections import Counter


def generate_recruiter_analytics(results):
    analytics = {}

    # Total resumes
    analytics["total_resumes"] = len(results)

    # Average match score
    if results:
        analytics["average_score"] = round(
            sum(r["score"] for r in results) / len(results), 2
        )
    else:
        analytics["average_score"] = 0

    # Strong hire count
    analytics["strong_hires"] = sum(
        1 for r in results if r["score"] >= 75
    )

    # Most common missing skills
    missing_skills = []
    for r in results:
        missing_skills.extend(r["missing"])

    if missing_skills:
        analytics["top_missing_skills"] = Counter(missing_skills).most_common(5)
    else:
        analytics["top_missing_skills"] = []

    # Best-fit role distribution
    roles = [r["best_role"] for r in results]
    analytics["role_distribution"] = Counter(roles)

    return analytics


if __name__ == "__main__":
    sample = [
        {"score": 80, "missing": ["sql"], "best_role": "Data Analyst"},
        {"score": 60, "missing": ["visualization"], "best_role": "ML Engineer"},
    ]
    print(generate_recruiter_analytics(sample))
