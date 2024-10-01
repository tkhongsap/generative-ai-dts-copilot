import os
import tempfile
import io
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

# Set page config
st.set_page_config(page_title="💡 D&T Meeting Summary", page_icon="📝", layout="wide")

# Apply custom CSS
st.markdown(get_meeting_summary_banner(), unsafe_allow_html=True)

# Initialize OpenAI API Key (ensure you have this in your environment or secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
                    # log_step("Preprocessing audio...", show=False)
                    preprocessed_path = preprocess_audio(file_path, temp_dir)
                    log_step("Audio preprocessing complete")
                    
                    # Step 2: Split audio into segments
                    # log_step("Splitting audio into segments...", show=False)
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

                    # Create tabs
                    tab1, tab2, tab3 = st.tabs(["Transcription", "Summary", "Detailed Report"])

                    # In the "Transcription" tab, display the full transcript
                    with tab1:
                        st.markdown(f"### Full Transcript: {uploaded_file.name}")
                        st.markdown(
                            f"""
                            <div style="max-height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;">
                            {full_transcript}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # In the "Summary" tab, display the summary content directly
                    with tab2:
                        if summary_content:
                            st.markdown(summary_content)
                        else:
                            st.error("Failed to generate summary. Please try again.")

                    # In the "Detailed Report" tab, display the detailed analysis
                    with tab3:
                        if detailed_report:
                            st.markdown("### Detailed Report")
                            st.markdown(detailed_report)
                        else:
                            st.error("Failed to generate detailed report. Please try again.")

            except Exception as e:
                st.sidebar.error(f"Error during processing: {str(e)}")
                st.exception(e)  # This will print the full traceback for debugging
    elif process_button and not uploaded_file:
        st.sidebar.warning("Please upload a file before processing.")

if __name__ == "__main__":
    main()