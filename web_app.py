"""Flask web app for the PowerPoint flashcard generator."""

import hashlib
import hmac
import os
import secrets
import tempfile

from flask import Flask, request, jsonify, session, render_template, redirect, url_for

from flashcard_generator.parser import extract_slides, format_slides_for_prompt
from flashcard_generator.generator import generate_flashcards

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# Password your friend uses to log in — set via environment variable
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")


def check_password(password: str) -> bool:
    if not APP_PASSWORD:
        return False
    return hmac.compare_digest(password, APP_PASSWORD)


@app.before_request
def require_login():
    open_paths = {"/login"}
    if request.path in open_paths or request.path.startswith("/static"):
        return
    if not session.get("authenticated"):
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    password = request.form.get("password", "")
    if check_password(password):
        session["authenticated"] = True
        session.permanent = True
        return redirect(url_for("index"))

    return render_template("login.html", error="Incorrect password.")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files["file"]
    if not file.filename or not file.filename.lower().endswith(".pptx"):
        return jsonify({"error": "Please upload a .pptx file."}), 400

    try:
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        slides = extract_slides(tmp_path)
        if not slides:
            return jsonify({"error": "No text content found in the presentation."}), 400

        slide_text = format_slides_for_prompt(slides)
        flashcards = generate_flashcards(slide_text)

        return jsonify({
            "flashcards": flashcards,
            "slide_count": len(slides),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if "tmp_path" in locals():
            os.unlink(tmp_path)


if __name__ == "__main__":
    if not APP_PASSWORD:
        print("WARNING: APP_PASSWORD is not set. No one will be able to log in.")
        print("Set it with: export APP_PASSWORD='your-password-here'")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY is not set. Generation will fail.")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")

    app.run(host="0.0.0.0", port=5000, debug=False)
