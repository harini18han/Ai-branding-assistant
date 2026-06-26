import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from fpdf import FPDF

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="AI Branding Assistant", page_icon="🚀")
st.title("AI Branding Assistant 🚀")

if not api_key:
    st.error("GROQ_API_KEY not found in .env file")
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

product = st.text_input("Enter your product idea:")
if st.button("Generate Branding ✨"):
    if not product:
        st.warning("Please enter a product idea!")
    else:
        with st.spinner("Generating your brand..."):

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

Marketing Strategy: (2-3  marketing strategy)

Social Media Post: (one engaging post for Instagram)
"""
                    }
                ]
            )
            branding_text = response.choices[0].message.content
            st.success("Your Brand is Ready! 🎉")
            st.markdown(response.choices[0].message.content)
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, branding_text)

            pdf.output("branding_report.pdf")

            with open("branding_report.pdf", "rb") as file:
                st.download_button(
                 label="📄 Download Branding Report",
                 data=file,
                 file_name="branding_report.pdf",
                 mime="application/pdf"
                )
