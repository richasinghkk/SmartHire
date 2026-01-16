from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import sqlite3
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
from models.analytics import generate_recruiter_analytics

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ---------------- APP CONFIG ----------------
app = Flask(__name__)
app.secret_key = "smarthire_secret_key"

UPLOAD_FOLDER = "data/resumes"
JD_PATH = "data/job_descriptions/jd.txt"
REPORT_FOLDER = "data/reports"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# ---------------- LANDING PAGE ----------------
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

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except:
            return render_template("register.html", error="User already exists")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- DASHBOARD (PROTECTED) ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    results = []
    analytics = None

    if request.method == "POST":
        files = request.files.getlist("resumes")

        with open(JD_PATH, "r", encoding="utf-8") as f:
            jd_text = f.read()

        for file in files:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            raw_text = parse_resume(filepath)
            bias_audit = generate_bias_audit(raw_text)
            cleaned_text = clean_text(raw_text)

            skills = extract_skills(cleaned_text)
            score = match_resume_with_jd(cleaned_text, jd_text)
            matched, missing = explain_match(cleaned_text, jd_text)
            experience = classify_experience(cleaned_text)
            advice = generate_resume_advice(missing, experience)
            role_scores, best_role = optimize_roles(cleaned_text)

            results.append({
                "name": file.filename,
                "score": score,
                "skills": skills,
                "experience": experience,
                "matched": matched,
                "missing": missing,
                "advice": advice,
                "bias_audit": bias_audit,
                "best_role": best_role
            })

        results = sorted(results, key=lambda x: x["score"], reverse=True)
        analytics = generate_recruiter_analytics(results)

    return render_template(
        "dashboard.html",
        results=results,
        analytics=analytics,
        user=session["user_name"]
    )

# ---------------- FEATURE PAGES ----------------
@app.route("/skills/<name>")
def skills_page(name):
    resume_path = os.path.join(UPLOAD_FOLDER, name)
    raw = parse_resume(resume_path)
    cleaned = clean_text(raw)
    skills = extract_skills(cleaned)
    return render_template("skills.html", name=name, skills=skills)

@app.route("/match/<name>")
def match_page(name):
    resume_path = os.path.join(UPLOAD_FOLDER, name)
    raw = parse_resume(resume_path)
    cleaned = clean_text(raw)

    with open(JD_PATH, "r", encoding="utf-8") as f:
        jd_text = f.read()

    matched, missing = explain_match(cleaned, jd_text)
    return render_template("match.html", name=name, matched=matched, missing=missing)

@app.route("/bias/<name>")
def bias_page(name):
    resume_path = os.path.join(UPLOAD_FOLDER, name)
    raw = parse_resume(resume_path)
    bias_report = generate_bias_audit(raw)
    return render_template("bias.html", name=name, bias=bias_report)

@app.route("/advice/<name>")
def advice_page(name):
    resume_path = os.path.join(UPLOAD_FOLDER, name)
    raw = parse_resume(resume_path)
    cleaned = clean_text(raw)

    experience = classify_experience(cleaned)
    with open(JD_PATH, "r", encoding="utf-8") as f:
        jd_text = f.read()

    _, missing = explain_match(cleaned, jd_text)
    advice = generate_resume_advice(missing, experience)

    return render_template("advice.html", name=name, advice=advice)

@app.route("/role/<name>")
def role_page(name):
    resume_path = os.path.join(UPLOAD_FOLDER, name)
    raw = parse_resume(resume_path)
    cleaned = clean_text(raw)

    role_scores, best_role = optimize_roles(cleaned)
    return render_template("role.html", name=name, role_scores=role_scores, best_role=best_role)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
