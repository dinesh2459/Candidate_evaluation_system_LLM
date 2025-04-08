from flask import Flask, request, jsonify, render_template
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pdfplumber
import docx
from werkzeug.utils import secure_filename
import ollama
from concurrent.futures import ThreadPoolExecutor
import time

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LLAMA_MODEL_NAME = "llama3.2"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "dsai96765@gmail.com"
EMAIL_PASSWORD = "cksu uzfq ejsg oqwt"
EMAIL_RECIPIENT = "dsai96765@gmail.com"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(file_paths):
    texts = {"interview": [], "coding": [], "other": []}

    def process_file(file_path):
        print(f"[INFO] Extracting text from {file_path}...")
        try:
            lines = []
            if file_path.endswith(".pdf"):
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            lines.extend(text.split("\n"))
            elif file_path.endswith(".docx"):
                doc = docx.Document(file_path)
                lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
            elif file_path.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]

            if "interview" in file_path.lower():
                return ("interview", lines)
            elif "coding" in file_path.lower():
                return ("coding", lines)
            else:
                return ("other", lines)

        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ("other", [])

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_file, file_paths))

    for category, lines in results:
        texts[category].extend(lines)

    print("[SUCCESS] Text extraction completed.")
    return texts

def summarize_text(texts, user_prompt):
    print("[INFO] Generating summary from extracted text...")

    prompt = f"""
    Analyze the following candidate evaluation data extracted from documents.

    Interview Transcript:
    {chr(10).join(texts['interview'])}

    Coding Assessment:
    {chr(10).join(texts['coding'])}

    Other Documents:
    {chr(10).join(texts['other'])}
    Instructions:
        user_prompt:{user_prompt}
        - Take candidate name from the interview transcript.
        - Provide a structured evaluation in the following format:
            -**Technical Skills** mentioned in user_prompt{user_prompt}
            -**Overall Rating** (Numeric value out of 5)
            -**Final Recommendation** (Based on Overall Rating):
                -"Hire" if rating > 3
                -"Hold" if rating == 3
                -"No Hire" if rating < 3
                -Justify your recommendation clearly in 2 lines.
    """

    try:
        response = ollama.generate(model=LLAMA_MODEL_NAME, prompt=prompt, stream=False, options={"max_tokens": 2000})
        print("[SUCCESS] Summary generation completed.")
        return response.get('response', 'Summary generation failed.').strip()
    except Exception as e:
        print(f"[ERROR] Ollama summarization failed: {e}")
        return f"Error during summarization: {e}"

def create_email_output(summary):
    print("[INFO] Formatting email content...")
    if "Error" in summary or not summary.strip():
        summary = "The document content was insufficient to generate a detailed evaluation. Please review the documents manually."

    email_body = f"""
    Subject: Candidate Evaluation Summary

    Dear Hiring Manager,

    Below is the structured candidate evaluation summary:

    {summary}

    Please review and proceed accordingly.

    Best regards,
    Recruitment Team
    """
    print("[SUCCESS] Email formatting completed.")
    return email_body.strip()

@app.route('/generate_email', methods=['POST'])
def generate_email_api():
    start_time = time.time()
    print("[INFO] Processing email generation request...")

    if 'files' not in request.files:
        return jsonify({'error': 'No files part in request'}), 400

    files = request.files.getlist('files')
    user_prompt = request.form.get('user_prompt', '').strip()

    if not files or all(file.filename.strip() == '' for file in files):
        return jsonify({'error': 'No selected files'}), 400

    def save_file(file):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            print(f"[SUCCESS] Saved file: {filename}")
            return path
        return None

    with ThreadPoolExecutor() as executor:
        file_paths = list(filter(None, executor.map(save_file, files)))

    if not file_paths:
        return jsonify({'error': 'No valid files uploaded.'}), 400

    extract_start = time.time()
    texts = extract_text(file_paths)
    print(f"[TIMER] Text extraction: {time.time() - extract_start:.2f}s")

    summarize_start = time.time()
    summary = summarize_text(texts, user_prompt)
    print(f"[TIMER] Summarization: {time.time() - summarize_start:.2f}s")

    email_output = create_email_output(summary)
    total_time = time.time() - start_time
    print(f"[SUCCESS] Total processing time: {total_time:.2f} seconds")

    return email_output

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_email', methods=['POST'])
def send_email():
    email_body = request.json.get('email_body', '').strip()
    if not email_body:
        return jsonify({'error': 'Email content is empty'}), 400

    subject = "Interview Evaluation Results"
    to_email = "rebalsai456@gmail.com"
    mailto_link = f"https://mail.google.com/mail/?view=cm&fs=1&tf=1&to={to_email}&su={subject}&body={email_body}"

    return jsonify({'mailto_link': mailto_link})

if __name__ == '__main__':
    print("[INFO] Starting Flask server...")
    app.run(debug=True, port=5000, threaded=True, use_reloader=True)









