import os
import tempfile
import io
import time
import streamlit as st
import base64
import streamlit.components.v1 as components

from utils.custom_css_banner import get_meeting_summary_banner
from pathlib import Path
from pydub import AudioSegment
import openai
import re
from utils.prompt_instructions import (
    get_summary_system_prompt,
    get_summary_user_prompt,
    get_detailed_report_system_prompt,
    get_detailed_report_user_prompt
)
import markdown
from utils.message_utils import message_func
from utils.openai_utils import generate_response
from openai import OpenAI

# Set page config
st.set_page_config(page_title="💡 D&T Meeting Summary", page_icon="📝", layout="wide")

# Apply custom CSS
st.markdown(get_meeting_summary_banner(), unsafe_allow_html=True)

# Initialize OpenAI API Key and client
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Modified logging function for the sidebar
def log_step(step_name, color="darkblue", show=True):
    if show:
        st.sidebar.markdown(f"<span style='color:{color};'>{step_name}</span>", unsafe_allow_html=True)

# Function to save uploaded file
def save_uploaded_file(uploaded_file, temp_dir):
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    temp_file_path = os.path.join(temp_dir, f"temp_input{file_extension}")
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(uploaded_file.read())
    return temp_file_path

# Function to preprocess audio
def preprocess_audio(file_path, temp_dir):
    audio = AudioSegment.from_file(file_path)
    
    # Convert to mono
    audio = audio.set_channels(1)
    
    # Normalize audio (adjust volume)
    audio = audio.normalize()
    
    # Remove silence at the beginning and end
    audio = audio.strip_silence(silence_len=1000, silence_thresh=-40)
    
    # Export as MP3 with a bitrate of 128kbps (adjust as needed)
    preprocessed_path = os.path.join(temp_dir, "preprocessed_audio.mp3")
    audio.export(preprocessed_path, format="mp3", bitrate="128k")
    
    return preprocessed_path

# Function to split MP3 audio into segments for easier processing
def split_audio(file_path, max_length=25*60*1000):  # 25 minutes in milliseconds
    audio = AudioSegment.from_mp3(file_path)
    segments = []
    
    # Split audio into 25-minute chunks (Whisper's maximum is 30 minutes)
    for i in range(0, len(audio), max_length):
        segment = audio[i:i+max_length]
        segments.append(segment)
    
    return segments

# Updated Function to transcribe audio using OpenAI's Whisper model
def transcribe_audio_segment(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    return transcription

# Function to post-process the transcript
def post_process_transcript(transcript):
    # Remove hesitation sounds
    transcript = re.sub(r'\b(um|uh|eh|ah)\b', '', transcript, flags=re.IGNORECASE)
    
    # Capitalize first letter of sentences
    transcript = '. '.join(sentence.capitalize() for sentence in transcript.split('. '))
    
    # Add periods at the end of sentences if missing
    transcript = re.sub(r'(?<=[a-z])\s+(?=[A-Z])', '. ', transcript)
    
    return transcript.strip()

def generate_summary(transcript):
    log_step("Generating summary...")
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": get_summary_system_prompt()},
                {"role": "user", "content": get_summary_user_prompt(transcript)}
            ],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None


def generate_detailed_report(transcript):
    log_step("Generating detailed report...")
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": get_detailed_report_system_prompt()},
                {"role": "user", "content": get_detailed_report_user_prompt(transcript)}
            ],
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating detailed report: {str(e)}")
        return None

# Function to handle file uploads and processing
def main():
    # Move file upload and process button to sidebar
    st.sidebar.subheader("Upload Audio or Video File", divider="rainbow")
    uploaded_file = st.sidebar.file_uploader(" ", type=['mp3', 'mp4', 'm4a', 'wav', 'avi'])

    process_button = st.sidebar.button("📝 Process File")

    if uploaded_file and process_button:
        with st.spinner("Processing..."):
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Step 1: Save uploaded file
                    file_path = save_uploaded_file(uploaded_file, temp_dir)
                    
                    # Preprocess audio
                    preprocessed_path = preprocess_audio(file_path, temp_dir)
                    log_step("Audio preprocessing complete")
                    
                    # Step 2: Split audio into segments
                    audio_segments = split_audio(preprocessed_path)
                    log_step(f"Split audio into {len(audio_segments)} segments.")

                    # Step 3: Transcribe each segment using Whisper
                    full_transcript = ""
                    log_step("Transcribing Audio Segments:")
                    progress_bar = st.progress(0)
                    transcription_status = st.sidebar.empty()
                    for i, segment in enumerate(audio_segments):
                        segment_file_path = os.path.join(temp_dir, f"segment_{i+1:02d}.mp3")
                        segment.export(segment_file_path, format="mp3", bitrate="128k")

                        transcription_status.text(f"Transcribing segment {i+1} of {len(audio_segments)}...")
                        transcript = transcribe_audio_segment(segment_file_path)
                        processed_transcript = post_process_transcript(transcript)
                        
                        full_transcript += processed_transcript + " "
                        progress_bar.progress((i + 1) / len(audio_segments))

                    log_step("Transcription complete")

                    # Generate summary and detailed report
                    log_step("Generating summary...")
                    summary_content = generate_summary(full_transcript)
                    log_step("Generating detailed report...")
                    detailed_report = generate_detailed_report(full_transcript)

                    # Save processed data to st.session_state
                    st.session_state['full_transcript'] = full_transcript
                    st.session_state['summary_content'] = summary_content
                    st.session_state['detailed_report'] = detailed_report
                    st.session_state['processing_completed'] = True

                    # Save the transcript to a temporary file with a proper extension
                    transcript_file_path = os.path.join(temp_dir, "transcript.txt")
                    with open(transcript_file_path, "w", encoding="utf-8") as f:
                        f.write(full_transcript)

                    # Upload the file with the correct filename
                    with open(transcript_file_path, "rb") as f:
                        transcript_file = client.files.create(
                            file=f,
                            purpose='assistants'
                        )
                    transcript_file_id = transcript_file.id

                    # Ensure the file is processed before proceeding
                    file_status = client.files.retrieve(transcript_file_id).status
                    while file_status != 'processed':
                        time.sleep(1)
                        file_status = client.files.retrieve(transcript_file_id).status

                    # Save the processed file ID to session state
                    st.session_state['transcript_file_id'] = transcript_file_id

            except Exception as e:
                st.sidebar.error(f"Error during processing: {str(e)}")
                st.exception(e)
    elif process_button and not uploaded_file:
        st.sidebar.warning("Please upload a file before processing.")

    # Display content if processing has been completed
    if st.session_state.get('processing_completed', False):
        display_processed_content()

    # --- Chat Interface Section ---
    display_chat_interface()

def display_processed_content():
    # Create tabs with custom CSS for better visibility
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            border-radius: 4px 4px 0px 0px;
            padding-top: 10px;
            padding-bottom: 10px;
            padding-left: 20px;
            padding-right: 20px;
            color: #5F6368;
            font-weight: 400;
        }
        .stTabs [aria-selected="true"] {
            background-color: transparent;
            color: #4285F4;
            font-weight: 500;
            border-bottom: 2px solid #4285F4;
        }
        </style>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Transcription", "Summary", "Detailed Report"])

    with tab1:
        st.markdown(f"### 📄 Transcript")
        transcript_html = markdown.markdown(st.session_state['full_transcript'])
        components.html(create_content_with_copy_button("transcript", transcript_html), height=700, scrolling=True)

    with tab2:
        st.markdown("### 📊 Summary")
        if st.session_state['summary_content']:
            summary_html = markdown.markdown(st.session_state['summary_content'])
            components.html(create_content_with_copy_button("summary", summary_html), height=700, scrolling=True)
        else:
            st.error("Failed to generate summary. Please try again.")

    with tab3:
        st.markdown("### 📑 Detailed Report")
        if st.session_state['detailed_report']:
            report_html = markdown.markdown(st.session_state['detailed_report'])
            components.html(create_content_with_copy_button("report", report_html), height=700, scrolling=True)
        else:
            st.error("Failed to generate detailed report. Please try again.")

def create_content_with_copy_button(content_type, content_html):
    return f"""
    <div style="
        background-color: #F8F9FA;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    ">
        <h4 style="margin: 0; color: #202124;">{content_type.capitalize()} Content</h4>
    </div>
    <div id="{content_type}-content" style="
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #E8EAED;
        padding: 15px;
        background-color: white;
        font-size: 14px;
        line-height: 1.6;
        border-radius: 4px;
    ">
    {content_html}
    </div>
    <div style="text-align: right; margin-top: 10px;">
        <button id="copy-{content_type}-button" style="
            background-color: #F1F3F4;
            color: #5F6368;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            font-size: 14px;
        ">
            <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#5F6368" style="margin-right: 4px;">
                <path d="M0 0h24v24H0z" fill="none"/>
                <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
            </svg>
            Copy
        </button>
    </div>
    <script>
    const copyButton_{content_type} = document.getElementById('copy-{content_type}-button');
    const content_{content_type} = document.getElementById('{content_type}-content');

    copyButton_{content_type}.addEventListener('click', () => {{
        const textToCopy = content_{content_type}.innerText;
        if (navigator.clipboard && window.isSecureContext) {{
            // navigator.clipboard API method
            navigator.clipboard.writeText(textToCopy).then(() => {{
                // Change button to indicate success
                copyButton_{content_type}.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#4285F4" style="margin-right: 4px;">
                        <path d="M0 0h24v24H0z" fill="none"/>
                        <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
                    </svg>
                    Copied!
                `;
                copyButton_{content_type}.style.backgroundColor = '#E8F0FE';
                copyButton_{content_type}.style.color = '#4285F4';

                setTimeout(() => {{
                    copyButton_{content_type}.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#5F6368" style="margin-right: 4px;">
                            <path d="M0 0h24v24H0z" fill="none"/>
                            <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                        </svg>
                        Copy
                    `;
                    copyButton_{content_type}.style.backgroundColor = '#F1F3F4';
                    copyButton_{content_type}.style.color = '#5F6368';
                }}, 2000);
            }})
            .catch(err => {{
                console.error('Failed to copy: ', err);
            }});
        }} else {{
            // Fallback method
            const textArea = document.createElement('textarea');
            textArea.value = textToCopy;
            document.body.appendChild(textArea);
            textArea.select();
            try {{
                document.execCommand('copy');
                // Change button to indicate success
                copyButton_{content_type}.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#4285F4" style="margin-right: 4px;">
                        <path d="M0 0h24v24H0z" fill="none"/>
                        <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
                    </svg>
                    Copied!
                `;
                copyButton_{content_type}.style.backgroundColor = '#E8F0FE';
                copyButton_{content_type}.style.color = '#4285F4';

                setTimeout(() => {{
                    copyButton_{content_type}.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#5F6368" style="margin-right: 4px;">
                            <path d="M0 0h24v24H0z" fill="none"/>
                            <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                        </svg>
                        Copy
                    `;
                    copyButton_{content_type}.style.backgroundColor = '#F1F3F4';
                    copyButton_{content_type}.style.color = '#5F6368';
                }}, 2000);
            }} catch (err) {{
                console.error('Fallback: Oops, unable to copy', err);
            }}
            document.body.removeChild(textArea);
        }}
    }});
    </script>
    """

def display_chat_interface():
    # Set assistant id (meeting summary assistant)
    assistant_id = "asst_xPItAapKJu36iVy0D9AwdOZ7"  # Replace with your assistant ID

    # Clear other assistants' message history
    for key in ['chat_assistant_messages', 'coding_assistant_messages', 'requirement_translator_messages']:
        if key in st.session_state:
            del st.session_state[key]

    # Initialize chat history
    if "meeting_summary_messages" not in st.session_state:
        st.session_state["meeting_summary_messages"] = [
            {"role": "assistant", "content": "👋 Hello! I'm your Meeting Summary Assistant. How can I help you with the meeting transcript and summary?"}
        ]

    # Load user and assistant icons
    def get_image_base64(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"

    user_icon_path = "image/user_icon.png"
    assistant_icon_path = "image/assistant_icon.png"
    user_icon_base64 = get_image_base64(user_icon_path)
    assistant_icon_base64 = get_image_base64(assistant_icon_path)

    # Display the chat history
    for message in st.session_state["meeting_summary_messages"]:
        is_user = message["role"] == "user"
        message_func(message["content"], user_icon_base64, assistant_icon_base64, is_user=is_user)

    # Accept user input
    prompt = st.chat_input("Your message")

    # Handle user input
    if prompt:
        st.session_state["meeting_summary_messages"].append({"role": "user", "content": prompt})
        message_func(prompt, user_icon_base64, assistant_icon_base64, is_user=True)

        # Retrieve the transcript file ID from session state
        transcript_file_id = st.session_state.get("transcript_file_id")

        # Generate a response using the assistant and pass the transcript file ID if available
        response = generate_response(prompt, assistant_id, transcript_file_id)

        st.session_state["meeting_summary_messages"].append({"role": "assistant", "content": response})
        message_func(response, user_icon_base64, assistant_icon_base64)

if __name__ == "__main__":
    main()