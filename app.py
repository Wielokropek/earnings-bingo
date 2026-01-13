import streamlit as st
import google.generativeai as genai
import random

# --- SETUP ---
st.set_page_config(page_title="Earnings Bingo", layout="wide")

# This safely gets your API key from the app settings later
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Please add your Gemini API Key to the secrets!")

# --- APP INTERFACE ---
st.title("🎯 Earnings Call Bingo")
st.write("Paste a transcript below to generate your custom Bingo board.")

# User pastes the transcript manually (Avoids expensive/complex automated data APIs)
transcript_input = st.text_area("Paste the Earnings Call Transcript here:", height=200, placeholder="Copy text from Motley Fool or Seeking Alpha...")

if st.button("Generate Bingo Board"):
    if transcript_input:
        with st.spinner("AI is hunting for buzzwords..."):
            model = genai.GenerativeModel('gemini-2.0-flash')
            prompt = f"Extract 25 unique corporate buzzwords or repetitive cliches from this transcript. Return ONLY a comma-separated list of 25 words. Transcript: {transcript_input[:15000]}"
            
            response = model.generate_content(prompt)
            words = [w.strip() for w in response.text.split(",")]
            
            # Store words in 'session state' so they don't disappear
            st.session_state.bingo_words = words[:25]
            st.session_state.marked = [False] * 25
    else:
        st.warning("Please paste a transcript first!")

# --- THE BINGO GRID ---
if "bingo_words" in st.session_state:
    st.write("---")
    st.subheader("Click the squares as you hear the words!")
    
    # Create a 5x5 grid
    cols = st.columns(5)
    for i in range(25):
        with cols[i % 5]:
            button_label = st.session_state.bingo_words[i]
            # If clicked, toggle the 'marked' status
            if st.button(button_label, key=f"btn_{i}", use_container_width=True, 
                         type="primary" if st.session_state.marked[i] else "secondary"):
                st.session_state.marked[i] = not st.session_state.marked[i]
                st.rerun()
