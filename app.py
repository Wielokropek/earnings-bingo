import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
import random

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Earnings Bingo", layout="wide", page_icon="🎯")

# Styling to make it look like a Bingo Card
st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 100px;
        font-weight: bold;
        font-size: 16px;
        white-space: normal;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API KEY SETUP ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing API Key! Please add 'GEMINI_API_KEY' to your Streamlit Secrets.")

# --- 3. THE APP INTERFACE ---
st.title("🎯 Earnings Call Bingo")
st.write("Turn dry corporate financial calls into a fun game!")

# Text area for user to paste transcript
transcript_input = st.text_area(
    "Paste the Earnings Call Transcript here:", 
    height=200, 
    placeholder="Copy text from a site like Motley Fool or Seeking Alpha..."
)

# --- 4. LOGIC TO GENERATE WORDS ---
if st.button("Generate Bingo Board"):
    if transcript_input:
        with st.spinner("Analyzing transcript... Please wait (this can take 10-20 seconds)."):
            try:
                # Using 1.5-flash as it is more reliable for free tier accounts
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = (
                    "Act as a financial analyst. Analyze this earnings call transcript. "
                    "Extract exactly 25 unique corporate buzzwords, cliches, or repetitive "
                    "business jargon phrases used. Return ONLY a comma-separated list of "
                    "the 25 items. No introduction, no numbers. "
                    f"Transcript: {transcript_input[:20000]}"
                )
                
                response = model.generate_content(prompt)
                
                # Turn the comma-separated text into a Python list
                raw_words = response.text.split(",")
                clean_words = [w.strip() for w in raw_words if w.strip()]
                
                # Make sure we have at least 25
                if len(clean_words) >= 25:
                    st.session_state.bingo_words = clean_words[:25]
                    st.session_state.marked = [False] * 25
                    st.success("Bingo Board Ready!")
                else:
                    st.error("The AI didn't find enough buzzwords. Try pasting more text.")

            except exceptions.ResourceExhausted:
                st.error("⚠️ GOOGLE QUOTA FULL: The free tier is busy. Please wait 60 seconds and click Generate again.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
    else:
        st.warning("Please paste a transcript first!")

# --- 5. THE BINGO GRID RENDERING ---
if "bingo_words" in st.session_state:
    st.write("---")
    st.subheader("Click a word to mark it!")
    
    # Create the 5x5 grid layout
    for row in range(5):
        cols = st.columns(5)
        for col in range(5):
            idx = row * 5 + col
            word = st.session_state.bingo_words[idx]
            is_marked = st.session_state.marked[idx]
            
            # Button color changes if marked (Primary = Red/Orange, Secondary = Gray)
            button_type = "primary" if is_marked else "secondary"
            
            if cols[col].button(word, key=f"cell_{idx}", use_container_width=True, type=button_type):
                st.session_state.marked[idx] = not st.session_state.marked[idx]
                st.rerun()

    # Reset Button
    if st.button("Clear Board"):
        del st.session_state.bingo_words
        st.rerun()
