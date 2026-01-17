from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

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
app.secret_key = "smarthire_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "resumes")
JD_PATH = os.path.join(BASE_DIR, "data", "job_descriptions", "jd.txt")

ALLOWED_EXTENSIONS = {"pdf", "docx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- HELPERS ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Email already exists")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
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

        if not files:
            return render_template(
                "dashboard.html",
                results=[],
                user=session["user_name"],
                error="No files uploaded"
            )

        with open(JD_PATH, "r", encoding="utf-8") as f:
            jd_text = f.read()

        for file in files:
            if file.filename == "" or not allowed_file(file.filename):
                continue

            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            try:
                raw_text = parse_resume(filepath)

                if not raw_text.strip():
                    continue

                cleaned_text = clean_text(raw_text)

                skills = extract_skills(cleaned_text)
                score = match_resume_with_jd(cleaned_text, jd_text)
                matched, missing = explain_match(cleaned_text, jd_text)
                experience = classify_experience(cleaned_text)
                advice = generate_resume_advice(missing, experience)
                _, best_role = optimize_roles(cleaned_text)

                results.append({
                    "name": filename,
                    "score": score,
                    "skills": skills,
                    "experience": experience,
                    "matched": matched,
                    "missing": missing,
                    "advice": advice,
                    "best_role": best_role
                })

            except Exception as e:
                print("❌ Resume error:", e)

        results.sort(key=lambda x: x["score"], reverse=True)

    return render_template(
        "dashboard.html",
        results=results,
        user=session["user_name"]
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
