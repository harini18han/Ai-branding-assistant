from flask import Flask, request, jsonify, send_from_directory, send_file
from openai import OpenAI
from dotenv import load_dotenv
import os
from fpdf import FPDF
import uuid

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

app = Flask(__name__, static_folder='static', static_url_path='/static')

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

if not os.path.exists('pdfs'):
    os.makedirs('pdfs')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/generate', methods=['POST'])
def generate_branding():
    if not api_key:
        return jsonify({"error": "GROQ_API_KEY not found"}), 500

    data = request.get_json()
    product = data.get('product')

    if not product:
        return jsonify({"error": "Product idea is required"}), 400

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": f"""
You are a branding expert.

For this product: {product}

Generate exactly:

Brand Name: (one catchy name)

Logo Prompt: (Create a professional AI image generation prompt for the logo)

Slogan: (one short slogan)

Caption: (one instagram caption)

Hashtags: (5 relevant hashtags)

Target Audience: (describe the ideal customer)

Brand Colors: (3-5 colors that represent the brand)

Marketing Strategy: (2-3 marketing strategy)

Social Media Post: (one engaging post for Instagram)
"""
                }
            ]
        )
        branding_text = response.choices[0].message.content

        pdf_filename = f"branding_report_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join("pdfs", pdf_filename)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)
        safe_text = branding_text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, safe_text)
        pdf.output(pdf_path)

        return jsonify({
            "branding_text": branding_text,
            "pdf_url": f"/api/download/{pdf_filename}"
        })

    except Exception as e:
        print(f"Error generating branding: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<filename>')
def download_pdf(filename):
    return send_file(os.path.join("pdfs", filename), as_attachment=True, download_name="branding_report.pdf")

@app.route('/api/chat', methods=['POST'])
def chat():
    if not api_key:
        return jsonify({"error": "GROQ_API_KEY not found"}), 500

    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert branding consultant."
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )
        return jsonify({
            "response": response.choices[0].message.content
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import threading
import webbrowser

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

