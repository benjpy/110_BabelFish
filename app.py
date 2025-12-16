import streamlit as st
import tempfile
import os
from dotenv import load_dotenv
from utils import convert_to_mp3, cleanup_files, get_timestamp
from api_client import AudioTranslator

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Audio Translator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #333;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .output-box {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .output-label {
        font-weight: 600;
        color: #555;
        margin-bottom: 0.5rem;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'transcript_text' not in st.session_state:
    st.session_state.transcript_text = None
if 'translation_text' not in st.session_state:
    st.session_state.translation_text = None
if 'timestamp' not in st.session_state:
    st.session_state.timestamp = None
if 'input_code' not in st.session_state:
    st.session_state.input_code = None
if 'target_code' not in st.session_state:
    st.session_state.target_code = None
if 'target_language_name' not in st.session_state:
    st.session_state.target_language_name = None

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # API Key Logic
    # 1. Try to get key from secrets
    secrets_api_key = None
    try:
        if "OPENAI_API_KEY" in st.secrets:
            secrets_api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

    # 2. Try environment variable if not in secrets
    if not secrets_api_key and "OPENAI_API_KEY" in os.environ:
        secrets_api_key = os.environ["OPENAI_API_KEY"]

    # 3. Sidebar Input (allows override)
    user_api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key here. Leave empty to use the system key if available.")
    
    # Final Key Determination
    api_key = user_api_key.strip().strip('"').strip("'")
    
    if not api_key:
        api_key = secrets_api_key

    # Status Indicators
    if api_key:
        if api_key == secrets_api_key and not user_api_key:
             st.success("✅ Using system API key", icon="🔐")
        else:
             st.success("✅ Using user-provided API key", icon="👤")
        
        # Debug Info (Safe)
        with st.expander("🔑 Key Debug Info"):
             st.write(f"Key Length: {len(api_key)}")
             st.write(f"Prefix: {api_key[:7]}...")
             st.write(f"Suffix: ...{api_key[-4:]}")
    else:
        st.warning("⚠️ No API Key found based. Please enter one.")
    
    st.markdown("---")
    st.markdown("### Language Options")
    
    languages = {
        "English": "en", "Spanish": "es", "French": "fr", "German": "de",
        "Italian": "it", "Portuguese": "pt", "Chinese": "zh", "Japanese": "ja",
        "Korean": "ko", "Russian": "ru", "Arabic": "ar", "Hindi": "hi"
    }
    
    input_lang_options = ["Auto-detect"] + list(languages.keys())
    input_language = st.selectbox(
        "Input Language (Original):",
        options=input_lang_options,
        index=0
    )
    
    target_language = st.selectbox(
        "Translate to (Output):",
        options=list(languages.keys()),
        index=0
    )

# Main UI
st.markdown("<h1 class='main-header'>🎙️ Audio Translator</h1>", unsafe_allow_html=True)
st.write("Upload an audio file (opus, m4a, mp3, mp4, wav) to transcribe and translate it.")

uploaded_file = st.file_uploader("Choose an audio file", type=["opus", "m4a", "mp3", "mp4", "wav"])

if uploaded_file is not None:
    st.audio(uploaded_file)
    
    if st.button("Transcribe & Translate", type="primary"):
        if not api_key:
            st.error("Please enter your OpenAI API Key in the sidebar.")
        else:
            tmp_file_path = None
            mp3_file_path = None
            
            try:
                translator = AudioTranslator(api_key)
                
                with st.spinner("Processing audio..."):
                    # Save temp file
                    file_ext = os.path.splitext(uploaded_file.name)[1]
                    if not file_ext:
                        file_ext = ".opus" # Default fallback

                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                    # Convert
                    st.info("Converting audio format...")
                    mp3_file_path = convert_to_mp3(tmp_file_path)

                    # Transcribe
                    st.info("Transcribing...")
                    lang_code = languages[input_language] if input_language != "Auto-detect" else None
                    transcript_text = translator.transcribe(mp3_file_path, lang_code)
                    
                    # Translate
                    st.info(f"Translating to {target_language}...")
                    translation_text = translator.translate(transcript_text, target_language)
                    
                    st.success("Processing complete!")

                    # Update Session State
                    st.session_state.transcript_text = transcript_text
                    st.session_state.translation_text = translation_text
                    st.session_state.timestamp = get_timestamp()
                    st.session_state.input_code = lang_code if lang_code else "original"
                    st.session_state.target_code = languages[target_language]
                    st.session_state.target_language_name = target_language

            except Exception as e:
                st.error("An error occurred during processing:")
                st.exception(e)
            finally:
                cleanup_files([tmp_file_path, mp3_file_path])

    # Display Results
    if st.session_state.transcript_text:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='output-box'>", unsafe_allow_html=True)
            st.markdown(f"<span class='output-label'>Original Transcript</span>", unsafe_allow_html=True)
            st.write(st.session_state.transcript_text)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.download_button(
                label="Download Transcript",
                data=st.session_state.transcript_text,
                file_name=f"transcript_{st.session_state.input_code}_{st.session_state.timestamp}.txt",
                mime="text/plain"
            )
            
        with col2:
            st.markdown("<div class='output-box'>", unsafe_allow_html=True)
            st.markdown(f"<span class='output-label'>Translation ({st.session_state.target_language_name})</span>", unsafe_allow_html=True)
            st.write(st.session_state.translation_text)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.download_button(
                label="Download Translation",
                data=st.session_state.translation_text,
                file_name=f"transcript_{st.session_state.target_code}_{st.session_state.timestamp}.txt",
                mime="text/plain"
            )

else:
    st.info("👆 Upload a file to get started.")
    if st.session_state.transcript_text:
        st.session_state.transcript_text = None
