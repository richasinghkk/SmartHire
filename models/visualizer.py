import matplotlib.pyplot as plt
import os


def generate_skill_gap_chart(top_missing_skills, output_path):
    if not top_missing_skills:
        return

    skills = [s[0] for s in top_missing_skills]
    counts = [s[1] for s in top_missing_skills]

    plt.figure()
    plt.barh(skills, counts)
    plt.xlabel("Frequency")
    plt.title("Top Missing Skills")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def generate_role_distribution_chart(role_distribution, output_path):
    roles = list(role_distribution.keys())
    counts = list(role_distribution.values())

    plt.figure()
    plt.pie(counts, labels=roles, autopct="%1.1f%%")
    plt.title("Best Fit Role Distribution")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def generate_score_distribution(scores, output_path):
    plt.figure()
    plt.hist(scores, bins=10)
    plt.xlabel("Match Score")
    plt.ylabel("Number of Candidates")
    plt.title("Score Distribution")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
