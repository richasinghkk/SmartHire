def generate_resume_advice(missing_skills, experience_level):
    advice = []

    if missing_skills:
        advice.append(
            f"Consider adding projects or experience related to: {', '.join(missing_skills[:5])}."
        )

    if experience_level == "Fresher":
        advice.append(
            "Add academic projects, internships, or certifications to strengthen your profile."
        )
        advice.append(
            "Use strong action verbs and clearly mention technologies used in projects."
        )
    else:
        advice.append(
            "Quantify your achievements using metrics (e.g., improved accuracy by 20%)."
        )
        advice.append(
            "Highlight leadership, system design, or optimization work."
        )

    advice.append(
        "Ensure your resume is ATS-friendly: use standard headings, bullet points, and avoid images."
    )

    return advice


if __name__ == "__main__":
    print(
        generate_resume_advice(
            ["data visualization", "statistics", "power bi"], "Fresher"
        )
    )
