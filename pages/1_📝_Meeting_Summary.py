# import os
# import tempfile
# import io
# import streamlit as st

# import base64
# import streamlit.components.v1 as components

# from utils.custom_css_banner import get_meeting_summary_banner

# from pathlib import Path
# from pydub import AudioSegment
# import openai
# import re

# from utils.prompt_instructions import (
#     get_summary_system_prompt,
#     get_summary_user_prompt,
#     get_detailed_report_system_prompt,
#     get_detailed_report_user_prompt
# )

# # Set page config
# st.set_page_config(page_title="💡 D&T Meeting Summary", page_icon="📝", layout="wide")

# # Apply custom CSS
# st.markdown(get_meeting_summary_banner(), unsafe_allow_html=True)

# # Initialize OpenAI API Key (ensure you have this in your environment or secrets)
# openai.api_key = st.secrets["OPENAI_API_KEY"]

# # Modified logging function for the sidebar
# def log_step(step_name, color="darkblue", show=True):
#     if show:
#         st.sidebar.markdown(f"<span style='color:{color};'>{step_name}</span>", unsafe_allow_html=True)

# # Function to save uploaded file
# def save_uploaded_file(uploaded_file, temp_dir):
#     file_extension = os.path.splitext(uploaded_file.name)[1].lower()
#     temp_file_path = os.path.join(temp_dir, f"temp_input{file_extension}")
#     with open(temp_file_path, "wb") as temp_file:
#         temp_file.write(uploaded_file.read())
#     return temp_file_path

# # Function to preprocess audio
# def preprocess_audio(file_path, temp_dir):
#     audio = AudioSegment.from_file(file_path)
    
#     # Convert to mono
#     audio = audio.set_channels(1)
    
#     # Normalize audio (adjust volume)
#     audio = audio.normalize()
    
#     # Remove silence at the beginning and end
#     audio = audio.strip_silence(silence_len=1000, silence_thresh=-40)
    
#     # Export as MP3 with a bitrate of 128kbps (adjust as needed)
#     preprocessed_path = os.path.join(temp_dir, "preprocessed_audio.mp3")
#     audio.export(preprocessed_path, format="mp3", bitrate="128k")
    
#     return preprocessed_path

# # Function to split MP3 audio into segments for easier processing
# def split_audio(file_path, max_length=25*60*1000):  # 25 minutes in milliseconds
#     audio = AudioSegment.from_mp3(file_path)
#     segments = []
    
#     # Split audio into 25-minute chunks (Whisper's maximum is 30 minutes)
#     for i in range(0, len(audio), max_length):
#         segment = audio[i:i+max_length]
#         segments.append(segment)
    
#     return segments

# # Updated Function to transcribe audio using OpenAI's Whisper model
# def transcribe_audio_segment(audio_file_path):
#     with open(audio_file_path, "rb") as audio_file:
#         transcription = openai.audio.transcriptions.create(
#             model="whisper-1",
#             file=audio_file,
#             response_format="text"
#         )
#     return transcription

# # Function to post-process the transcript
# def post_process_transcript(transcript):
#     # Remove hesitation sounds
#     transcript = re.sub(r'\b(um|uh|eh|ah)\b', '', transcript, flags=re.IGNORECASE)
    
#     # Capitalize first letter of sentences
#     transcript = '. '.join(sentence.capitalize() for sentence in transcript.split('. '))
    
#     # Add periods at the end of sentences if missing
#     transcript = re.sub(r'(?<=[a-z])\s+(?=[A-Z])', '. ', transcript)
    
#     return transcript.strip()

# def generate_summary(transcript):
#     log_step("Generating summary...")
#     try:
#         response = openai.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": get_summary_system_prompt()},
#                 {"role": "user", "content": get_summary_user_prompt(transcript)}
#             ],
#             max_tokens=2000
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         st.error(f"Error generating summary: {str(e)}")
#         return None

# def generate_detailed_report(transcript):
#     log_step("Generating detailed report...")
#     try:
#         response = openai.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": get_detailed_report_system_prompt()},
#                 {"role": "user", "content": get_detailed_report_user_prompt(transcript)}
#             ],
#             max_tokens=4000
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         st.error(f"Error generating detailed report: {str(e)}")
#         return None

# # Function to handle file uploads and processing
# def main():
#     # Move file upload and process button to sidebar
#     st.sidebar.subheader("Upload Audio or Video File", divider="rainbow")
#     uploaded_file = st.sidebar.file_uploader(" ", type=['mp3', 'mp4', 'm4a', 'wav', 'avi'])

#     process_button = st.sidebar.button("📝 Process File")

#     if uploaded_file and process_button:
#         with st.spinner("Processing..."):
#             try:
#                 with tempfile.TemporaryDirectory() as temp_dir:
#                     # Step 1: Save uploaded file
#                     file_path = save_uploaded_file(uploaded_file, temp_dir)
                    
#                     # Preprocess audio
#                     # log_step("Preprocessing audio...", show=False)
#                     preprocessed_path = preprocess_audio(file_path, temp_dir)
#                     log_step("Audio preprocessing complete")
                    
#                     # Step 2: Split audio into segments
#                     # log_step("Splitting audio into segments...", show=False)
#                     audio_segments = split_audio(preprocessed_path)
#                     log_step(f"Split audio into {len(audio_segments)} segments.")

#                     # Step 3: Transcribe each segment using Whisper
#                     full_transcript = ""
#                     log_step("Transcribing Audio Segments:")
#                     progress_bar = st.progress(0)
#                     transcription_status = st.sidebar.empty()
#                     for i, segment in enumerate(audio_segments):
#                         segment_file_path = os.path.join(temp_dir, f"segment_{i+1:02d}.mp3")
#                         segment.export(segment_file_path, format="mp3", bitrate="128k")

#                         transcription_status.text(f"Transcribing segment {i+1} of {len(audio_segments)}...")
#                         transcript = transcribe_audio_segment(segment_file_path)
#                         processed_transcript = post_process_transcript(transcript)
                        
#                         full_transcript += processed_transcript + " "
#                         progress_bar.progress((i + 1) / len(audio_segments))

#                     log_step("Transcription complete")

#                     # Generate summary and detailed report
#                     log_step("Generating summary...")
#                     summary_content = generate_summary(full_transcript)
#                     log_step("Generating detailed report...")
#                     detailed_report = generate_detailed_report(full_transcript)

#                     # Create tabs with custom CSS for better visibility
#                     st.markdown("""
#                         <style>
#                         .stTabs [data-baseweb="tab-list"] {
#                             gap: 24px;
#                         }
#                         .stTabs [data-baseweb="tab"] {
#                             height: 50px;
#                             white-space: pre-wrap;
#                             border-radius: 4px 4px 0px 0px;
#                             padding-top: 10px;
#                             padding-bottom: 10px;
#                             padding-left: 20px;
#                             padding-right: 20px;
#                             color: #5F6368;
#                             font-weight: 400;
#                         }
#                         .stTabs [aria-selected="true"] {
#                             background-color: transparent;
#                             color: #4285F4;
#                             font-weight: 500;
#                             border-bottom: 2px solid #4285F4;
#                         }
#                         </style>""", unsafe_allow_html=True)

#                     tab1, tab2, tab3 = st.tabs(["Transcription", "Summary", "Detailed Report"])

#                     # Function to create copy button HTML
#                     def create_copy_button(button_id):
#                         return f"""
#                         <button id="{button_id}" style="
#                             background-color: #F1F3F4;
#                             color: #5F6368;
#                             border: none;
#                             padding: 8px 16px;
#                             border-radius: 4px;
#                             cursor: pointer;
#                             display: flex;
#                             align-items: center;
#                             font-size: 14px;
#                         ">
#                             <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#5F6368" style="margin-right: 4px;">
#                                 <path d="M0 0h24v24H0z" fill="none"/>
#                                 <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
#                             </svg>
#                             Copy
#                         </button>
#                         """

#                     # Function to create copy script
#                     def create_copy_script(button_id, content_id):
#                         return f"""
#                         <script>
#                         const copyButton_{button_id} = document.getElementById('{button_id}');
#                         const content_{content_id} = document.getElementById('{content_id}');

#                         copyButton_{button_id}.addEventListener('click', () => {{
#                             const textArea = document.createElement('textarea');
#                             textArea.value = content_{content_id}.innerText;
#                             document.body.appendChild(textArea);
#                             textArea.select();
#                             document.execCommand('copy');
#                             document.body.removeChild(textArea);
                            
#                             copyButton_{button_id}.innerHTML = `
#                                 <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#4285F4" style="margin-right: 4px;">
#                                     <path d="M0 0h24v24H0z" fill="none"/>
#                                     <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
#                                 </svg>
#                                 Copied!
#                             `;
#                             copyButton_{button_id}.style.backgroundColor = '#E8F0FE';
#                             copyButton_{button_id}.style.color = '#4285F4';
                            
#                             setTimeout(() => {{
#                                 copyButton_{button_id}.innerHTML = `
#                                     <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#5F6368" style="margin-right: 4px;">
#                                         <path d="M0 0h24v24H0z" fill="none"/>
#                                         <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
#                                     </svg>
#                                     Copy
#                                 `;
#                                 copyButton_{button_id}.style.backgroundColor = '#F1F3F4';
#                                 copyButton_{button_id}.style.color = '#5F6368';
#                             }}, 2000);
#                         }});
#                         </script>
#                         """

#                     # In the "Transcription" tab, display the full transcript
#                     with tab1:
#                         st.markdown(f"### 📄 Transcript: {uploaded_file.name}")
                        
#                         st.markdown(
#                             f"""
#                             <div style="
#                                 background-color: #F8F9FA;
#                                 border-radius: 8px;
#                                 padding: 20px;
#                                 box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
#                             ">
#                                 <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
#                                     <h4 style="margin: 0; color: #202124;">Transcript Content</h4>
#                                     {create_copy_button("copy-transcript-button")}
#                                 </div>
#                             </div>
#                             {create_copy_script("copy-transcript-button", "transcript-content")}
#                             """,
#                             unsafe_allow_html=True
#                         )
                        
#                         st.markdown(
#                             f"""
#                             <div id="transcript-content" style="
#                                 max-height: 400px;
#                                 overflow-y: auto;
#                                 border: 1px solid #E8EAED;
#                                 padding: 15px;
#                                 background-color: white;
#                                 font-size: 14px;
#                                 line-height: 1.6;
#                                 border-radius: 4px;
#                             ">
#                             {full_transcript}
#                             </div>
#                             """,
#                             unsafe_allow_html=True
#                         )

#                     # In the "Summary" tab, display the summary content
#                     with tab2:
#                         st.markdown("### 📊 Summary")
#                         if summary_content:
#                             st.markdown(
#                                 f"""
#                                 <div style="
#                                     background-color: #F8F9FA;
#                                     border-radius: 8px;
#                                     padding: 20px;
#                                     box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
#                                 ">
#                                     <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
#                                         <h4 style="margin: 0; color: #202124;">Summary Content</h4>
#                                         {create_copy_button("copy-summary-button")}
#                                     </div>
#                                 </div>
#                                 {create_copy_script("copy-summary-button", "summary-content")}
#                                 """,
#                                 unsafe_allow_html=True
#                             )
#                             st.markdown(
#                                 f"""
#                                 <div id="summary-content" style="
#                                     max-height: 400px;
#                                     overflow-y: auto;
#                                     border: 1px solid #E8EAED;
#                                     padding: 15px;
#                                     background-color: white;
#                                     font-size: 14px;
#                                     line-height: 1.6;
#                                     border-radius: 4px;
#                                 ">
#                                 {summary_content}
#                                 </div>
#                                 """,
#                                 unsafe_allow_html=True
#                             )
#                         else:
#                             st.error("Failed to generate summary. Please try again.")

#                     # In the "Detailed Report" tab, display the detailed analysis
#                     with tab3:
#                         st.markdown("### 📑 Detailed Report")
#                         if detailed_report:
#                             st.markdown(
#                                 f"""
#                                 <div style="
#                                     background-color: #F8F9FA;
#                                     border-radius: 8px;
#                                     padding: 20px;
#                                     box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
#                                 ">
#                                     <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
#                                         <h4 style="margin: 0; color: #202124;">Detailed Report Content</h4>
#                                         {create_copy_button("copy-report-button")}
#                                     </div>
#                                 </div>
#                                 {create_copy_script("copy-report-button", "report-content")}
#                                 """,
#                                 unsafe_allow_html=True
#                             )
#                             st.markdown(
#                                 f"""
#                                 <div id="report-content" style="
#                                     max-height: 400px;
#                                     overflow-y: auto;
#                                     border: 1px solid #E8EAED;
#                                     padding: 15px;
#                                     background-color: white;
#                                     font-size: 14px;
#                                     line-height: 1.6;
#                                     border-radius: 4px;
#                                 ">
#                                 {detailed_report}
#                                 </div>
#                                 """,
#                                 unsafe_allow_html=True
#                             )
#                         else:
#                             st.error("Failed to generate detailed report. Please try again.")

#             except Exception as e:
#                 st.sidebar.error(f"Error during processing: {str(e)}")
#                 st.exception(e)  # This will print the full traceback for debugging
#     elif process_button and not uploaded_file:
#         st.sidebar.warning("Please upload a file before processing.")

# if __name__ == "__main__":
#     main()

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

                    # Function to create copy button HTML
                    def create_copy_button(button_id):
                        return f"""
                        <button id="{button_id}" style="
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
                        """

                    # Function to create copy script with improved functionality
                    def create_copy_script(button_id, content_id):
                        return f"""
                        <script>
                        const copyButton_{button_id} = document.getElementById('{button_id}');
                        const content_{content_id} = document.getElementById('{content_id}');

                        copyButton_{button_id}.addEventListener('click', () => {{
                            const textToCopy = content_{content_id}.textContent;
                            if (navigator.clipboard && window.isSecureContext) {{
                                // navigator.clipboard API method
                                navigator.clipboard.writeText(textToCopy).then(() => {{
                                    // Change button to indicate success
                                    copyButton_{button_id}.innerHTML = `
                                        <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#4285F4" style="margin-right: 4px;">
                                            <path d="M0 0h24v24H0z" fill="none"/>
                                            <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
                                        </svg>
                                        Copied!
                                    `;
                                    copyButton_{button_id}.style.backgroundColor = '#E8F0FE';
                                    copyButton_{button_id}.style.color = '#4285F4';

                                    setTimeout(() => {{
                                        copyButton_{button_id}.innerHTML = `
                                            <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#5F6368" style="margin-right: 4px;">
                                                <path d="M0 0h24v24H0z" fill="none"/>
                                                <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                                            </svg>
                                            Copy
                                        `;
                                        copyButton_{button_id}.style.backgroundColor = '#F1F3F4';
                                        copyButton_{button_id}.style.color = '#5F6368';
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
                                    copyButton_{button_id}.innerHTML = `
                                        <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#4285F4" style="margin-right: 4px;">
                                            <path d="M0 0h24v24H0z" fill="none"/>
                                            <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
                                        </svg>
                                        Copied!
                                    `;
                                    copyButton_{button_id}.style.backgroundColor = '#E8F0FE';
                                    copyButton_{button_id}.style.color = '#4285F4';

                                    setTimeout(() => {{
                                        copyButton_{button_id}.innerHTML = `
                                            <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#5F6368" style="margin-right: 4px;">
                                                <path d="M0 0h24v24H0z" fill="none"/>
                                                <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                                            </svg>
                                            Copy
                                        `;
                                        copyButton_{button_id}.style.backgroundColor = '#F1F3F4';
                                        copyButton_{button_id}.style.color = '#5F6368';
                                    }}, 2000);
                                }} catch (err) {{
                                    console.error('Fallback: Oops, unable to copy', err);
                                }}
                                document.body.removeChild(textArea);
                            }}
                        }});
                        </script>
                        """

                    # In the "Transcription" tab, display the full transcript
                    with tab1:
                        st.markdown(f"### 📄 Transcript: {uploaded_file.name}")
                        
                        st.markdown(
                            f"""
                            <div style="
                                background-color: #F8F9FA;
                                border-radius: 8px;
                                padding: 20px;
                                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                            ">
                                <h4 style="margin: 0; color: #202124;">Transcript Content</h4>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        st.markdown(
                            f"""
                            <div id="transcript-content" style="
                                max-height: 400px;
                                overflow-y: auto;
                                border: 1px solid #E8EAED;
                                padding: 15px;
                                background-color: white;
                                font-size: 14px;
                                line-height: 1.6;
                                border-radius: 4px;
                            ">
                            {full_transcript}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Create the copy button aligned to the right
                        st.markdown(
                            f"""
                            <div style="text-align: right; margin-top: 10px;">
                                {create_copy_button("copy-transcript-button")}
                            </div>
                            {create_copy_script("copy-transcript-button", "transcript-content")}
                            """,
                            unsafe_allow_html=True
                        )

                    # In the "Summary" tab, display the summary content
                    with tab2:
                        st.markdown("### 📊 Summary")
                        if summary_content:
                            st.markdown(
                                f"""
                                <div style="
                                    background-color: #F8F9FA;
                                    border-radius: 8px;
                                    padding: 20px;
                                    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                                ">
                                    <h4 style="margin: 0; color: #202124;">Summary Content</h4>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"""
                                <div id="summary-content" style="
                                    max-height: 400px;
                                    overflow-y: auto;
                                    border: 1px solid #E8EAED;
                                    padding: 15px;
                                    background-color: white;
                                    font-size: 14px;
                                    line-height: 1.6;
                                    border-radius: 4px;
                                ">
                                {summary_content}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            # Create the copy button aligned to the right
                            st.markdown(
                                f"""
                                <div style="text-align: right; margin-top: 10px;">
                                    {create_copy_button("copy-summary-button")}
                                </div>
                                {create_copy_script("copy-summary-button", "summary-content")}
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.error("Failed to generate summary. Please try again.")

                    # In the "Detailed Report" tab, display the detailed analysis
                    with tab3:
                        st.markdown("### 📑 Detailed Report")
                        if detailed_report:
                            st.markdown(
                                f"""
                                <div style="
                                    background-color: #F8F9FA;
                                    border-radius: 8px;
                                    padding: 20px;
                                    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                                ">
                                    <h4 style="margin: 0; color: #202124;">Detailed Report Content</h4>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"""
                                <div id="report-content" style="
                                    max-height: 400px;
                                    overflow-y: auto;
                                    border: 1px solid #E8EAED;
                                    padding: 15px;
                                    background-color: white;
                                    font-size: 14px;
                                    line-height: 1.6;
                                    border-radius: 4px;
                                ">
                                {detailed_report}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            # Create the copy button aligned to the right
                            st.markdown(
                                f"""
                                <div style="text-align: right; margin-top: 10px;">
                                    {create_copy_button("copy-report-button")}
                                </div>
                                {create_copy_script("copy-report-button", "report-content")}
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.error("Failed to generate detailed report. Please try again.")

            except Exception as e:
                st.sidebar.error(f"Error during processing: {str(e)}")
                st.exception(e)  # This will print the full traceback for debugging
    elif process_button and not uploaded_file:
        st.sidebar.warning("Please upload a file before processing.")

if __name__ == "__main__":
    main()
