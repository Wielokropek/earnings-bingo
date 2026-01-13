import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Earnings Bingo 2026", layout="wide", page_icon="🎯")

# Custom CSS for the Bingo Grid
st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 100px;
        font-weight: bold;
        font-size: 16px;
        white-space: normal;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API KEY SETUP ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing API Key! Go to Streamlit Settings > Secrets and add GEMINI_API_KEY.")

# --- 3. THE APP INTERFACE ---
st.title("🎯 Earnings Call Bingo")
st.write("Analyze the latest corporate jargon and play along!")

transcript_input = st.text_area(
    "Paste the Earnings Call Transcript here:", 
    height=200, 
    placeholder="Copy the text from Motley Fool, Seeking Alpha, or an IR page..."
)

# --- 4. LOGIC TO GENERATE WORDS ---
if st.button("Generate Bingo Board"):
    if transcript_input:
        with st.spinner("AI is scanning for cliches..."):
            try:
                # UPDATED FOR 2026: Using the stable gemini-2.5-flash model
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = (
                    "You are a corporate jargon expert. Analyze this earnings transcript. "
                    "Pick exactly 25 unique buzzwords, cliches, or repetitive business phrases "
                    "(e.g., 'Tailwinds', 'AI-driven', 'Synergies'). "
                    "Return ONLY a comma-separated list of 25 items. No other text."
                    f"\n\nTranscript: {transcript_input[:15000]}"
                )
                
                response = model.generate_content(prompt)
                
                # Split the AI response into a list of words
                words = [w.strip() for w in response.text.split(",") if w.strip()]
                
                if len(words) >= 25:
                    st.session_state.bingo_words = words[:25]
                    st.session_state.marked = [False] * 25
                    st.success("Board Generated!")
                else:
                    st.error(f"The AI only found {len(words)} words. Try pasting a longer transcript.")

            except exceptions.NotFound:
                st.error("❌ Model Error: It looks like this model version was just updated. Try changing 'gemini-2.5-flash' to 'gemini-3-flash' in the code.")
            except exceptions.ResourceExhausted:
                st.error("⚠️ Free limit reached. Wait 60 seconds and try again.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please paste a transcript first!")

# --- 5. THE BINGO GRID ---
if "bingo_words" in st.session_state:
    st.write("---")
    st.subheader("Click to mark your board:")
    
    # Create the 5x5 grid
    for row in range(5):
        cols = st.columns(5)
        for col in range(5):
            idx = row * 5 + col
            word = st.session_state.bingo_words[idx]
            is_marked = st.session_state.marked[idx]
            
            # Change color if clicked
            btn_type = "primary" if is_marked else "secondary"
            
            if cols[col].button(word, key=f"cell_{idx}", use_container_width=True, type=btn_type):
                st.session_state.marked[idx] = not st.session_state.marked[idx]
                st.rerun()

    if st.button("Start Over"):
        del st.session_state.bingo_words
        st.rerun()
