import streamlit as st
import tempfile
import os
from dotenv import load_dotenv
from utils import convert_opus_to_mp3, cleanup_files, get_timestamp
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

# ... (CSS remains the same)

# ... (Session state init remains the same)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Try to get key from secrets or environment
    default_api_key = ""
    try:
        if "OPENAI_API_KEY" in st.secrets:
            default_api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

    if not default_api_key and "OPENAI_API_KEY" in os.environ:
        default_api_key = os.environ["OPENAI_API_KEY"]

    api_key_input = st.text_input("OpenAI API Key", value=default_api_key, type="password", help="Enter your OpenAI API key here.")
    
    # Clean the key: remove whitespace and quotes
    api_key = api_key_input.strip().strip('"').strip("'")
    
    # Debug Info
    with st.expander("🔑 Key Debug Info"):
        if api_key:
            st.write(f"Key Length: {len(api_key)}")
            st.write(f"Prefix: {api_key[:7]}...")
            st.write(f"Suffix: ...{api_key[-4:]}")
            if api_key != api_key_input:
                st.info("ℹ️ Key was automatically cleaned (whitespace/quotes removed).")
        else:
            st.warning("No API Key detected.")
    
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
st.write("Upload an `.opus` audio file to transcribe and translate it.")

uploaded_file = st.file_uploader("Choose an audio file", type=["opus"])

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/opus')
    
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
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".opus") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                    # Convert
                    st.info("Converting audio format...")
                    mp3_file_path = convert_opus_to_mp3(tmp_file_path)

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
