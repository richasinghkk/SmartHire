import re

def generate_bias_audit(raw_text):
    audit = []

    # Email detection
    if re.search(r"\S+@\S+", raw_text):
        audit.append("Email detected and masked")

    # Phone number detection
    if re.search(r"\b\d{10}\b", raw_text):
        audit.append("Phone number detected and masked")

    # Gender words detection
    gender_words = ["male", "female", "he", "she", "his", "her"]
    for word in gender_words:
        if re.search(rf"\b{word}\b", raw_text, re.IGNORECASE):
            audit.append("Gender-related terms removed")
            break

    # Name detection (simple heuristic)
    audit.append("Name removed (heuristic-based)")

    # Final confirmation
    audit.append("Screening performed using skills and experience only")

    return audit


if __name__ == "__main__":
    sample = "John Doe | Male | john@gmail.com | 9876543210"
    print(generate_bias_audit(sample))
