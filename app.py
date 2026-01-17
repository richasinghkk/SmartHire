from flask import Flask, render_template, request, redirect, url_for, session
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

from resume_parser.parser import parse_resume
from preprocessing.text_cleaner import clean_text
from utils.helpers import extract_skills
from models.matcher import match_resume_with_jd
from models.explainer import explain_match
from models.classifier import classify_experience
from models.bias_audit import generate_bias_audit
from models.resume_advisor import generate_resume_advice
from models.role_optimizer import optimize_roles

# ---------------- APP CONFIG ----------------
app = Flask(__name__)
app.secret_key = "smarthire_secret_key"   # for sessions

UPLOAD_FOLDER = "data/resumes"
JD_PATH = "data/job_descriptions/jd.txt"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- MYSQL CONFIG ----------------
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1014",
    "database": "smarthire"
}

def get_db_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

# ---------------- LANDING ----------------
@app.route("/")
def landing():
    return render_template("landing.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            return render_template("register.html", error="All fields required")

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed_password)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for("login"))

        except mysql.connector.IntegrityError:
            return render_template("register.html", error="Email already exists")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    results = []

    if request.method == "POST":
        files = request.files.getlist("resumes")

        with open(JD_PATH, "r", encoding="utf-8") as f:
            jd_text = f.read()

        for file in files:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            raw_text = parse_resume(filepath)
            cleaned_text = clean_text(raw_text)

            skills = extract_skills(cleaned_text)
            score = match_resume_with_jd(cleaned_text, jd_text)
            matched, missing = explain_match(cleaned_text, jd_text)
            experience = classify_experience(cleaned_text)
            advice = generate_resume_advice(missing, experience)
            _, best_role = optimize_roles(cleaned_text)

            results.append({
                "name": file.filename,
                "score": score,
                "skills": skills,
                "experience": experience,
                "matched": matched,
                "missing": missing,
                "advice": advice,
                "best_role": best_role
            })

        results = sorted(results, key=lambda x: x["score"], reverse=True)

    return render_template(
        "dashboard.html",
        results=results,
        user=session["user_name"]
    )

# ---------------- FEATURE PAGES ----------------
@app.route("/skills/<name>")
def skills_page(name):
    raw = parse_resume(os.path.join(UPLOAD_FOLDER, name))
    skills = extract_skills(clean_text(raw))
    return render_template("skills.html", name=name, skills=skills)

@app.route("/match/<name>")
def match_page(name):
    raw = parse_resume(os.path.join(UPLOAD_FOLDER, name))
    cleaned = clean_text(raw)
    with open(JD_PATH, "r", encoding="utf-8") as f:
        jd_text = f.read()
    matched, missing = explain_match(cleaned, jd_text)
    return render_template("match.html", name=name, matched=matched, missing=missing)

@app.route("/bias/<name>")
def bias_page(name):
    raw = parse_resume(os.path.join(UPLOAD_FOLDER, name))
    bias_report = generate_bias_audit(raw)
    return render_template("bias.html", name=name, bias=bias_report)

@app.route("/advice/<name>")
def advice_page(name):
    raw = parse_resume(os.path.join(UPLOAD_FOLDER, name))
    cleaned = clean_text(raw)
    with open(JD_PATH, "r", encoding="utf-8") as f:
        jd_text = f.read()
    _, missing = explain_match(cleaned, jd_text)
    advice = generate_resume_advice(missing, classify_experience(cleaned))
    return render_template("advice.html", name=name, advice=advice)

@app.route("/role/<name>")
def role_page(name):
    raw = parse_resume(os.path.join(UPLOAD_FOLDER, name))
    cleaned = clean_text(raw)
    role_scores, best_role = optimize_roles(cleaned)
    return render_template("role.html", name=name, role_scores=role_scores, best_role=best_role)

# ---------------- RUN ----------------
# if __name__ == "__main__":
#     app.run(debug=True)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
