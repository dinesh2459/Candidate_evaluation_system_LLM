# 🧠 Candidate Evaluation Email Generator using LLaMA 3 (Ollama)
This project is a Flask-based web application that:

Uploads and extracts text from multiple documents (PDF, DOCX, TXT)
Summarizes interview and assessment results using LLaMA 3 (via Ollama)
Automatically generates a structured candidate evaluation email for HR
Optimized using parallel processing for fast document handling and summarization.

📦 Features
📂 Upload multiple interview, coding, and other evaluation files
🧠 Summarize content using LLaMA 3 (locally via Ollama)
📬 Generate a structured evaluation email with ratings and recommendations
⚡ Fast: Parallel file processing and summarization using ThreadPoolExecutor
🧰 Tech Stack
Python 3.8+
Flask (web framework)
Ollama (runs LLaMA 3 locally)
pdfplumber (PDF text extraction)
python-docx (DOCX file parsing)
ThreadPoolExecutor (for speed)
HTML/CSS (basic web form)
🚀 Installation
1. Clone the Repository
git clone https://github.com/your-username/candidate-evaluation-email-generator.git
cd candidate-evaluation-email-generator

### 2. Create a Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

### 3. Install Dependencies
pip install -r requirements.txt

🧠 Setting Up Ollama (LLaMA 3)
1. Install Ollama
# For Mac/Linux
curl -fsSL https://ollama.com/install.sh | sh
# For Windows: Download from https://ollama.com/download

2. Start Ollama Server
ollama run llama3

Start the Flask Server
python app.py

Open in your browser:
http://localhost:5000/

🧑‍💻 Author
Sai Dinesh
GitHub: @dinesh2459
