import os
import streamlit as st
import markdown
import PyPDF2
import docx
import pandas as pd
import streamlit.components.v1 as components
import openai

# Import your custom CSS functions
from utils.custom_css_banner import get_business_requirement_banner
from utils.custom_css_style import (
    get_content_container_style,
    get_content_style,
    get_copy_button_style
)
from utils.prompt_instructions import (
    get_business_requirement_system_prompt,
    get_business_requirement_user_prompt
)

# Set page configuration
st.set_page_config(
    page_title="💡 D&T Business Requirement Translator",
    page_icon="🔄",
    layout="wide"
)

# Apply custom CSS
st.markdown(get_business_requirement_banner(), unsafe_allow_html=True)
st.markdown(get_content_container_style(), unsafe_allow_html=True)  # Assuming this returns necessary CSS

# Initialize OpenAI API Key (ensure you have this in your environment or secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

def read_file_content(file):
    """
    Reads content from uploaded files based on their extension.
    Supports .txt, .pdf, .docx, .xlsx, and .xls files.
    Ensures proper encoding for Thai language support.
    """
    file_extension = os.path.splitext(file.name)[1].lower()
    content = ""

    try:
        if file_extension == '.txt':
            # Attempt to decode with UTF-8
            try:
                content = file.getvalue().decode('utf-8')
            except UnicodeDecodeError:
                # Fallback to other common encodings if UTF-8 fails
                try:
                    content = file.getvalue().decode('utf-16')
                except UnicodeDecodeError:
                    st.warning("Unable to decode the .txt file. Please ensure it's encoded in UTF-8 or UTF-16.")
        elif file_extension == '.pdf':
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    content += extracted_text + "\n"
        elif file_extension == '.docx':
            doc = docx.Document(file)
            for para in doc.paragraphs:
                content += para.text + "\n"
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file)
            content = df.to_string(index=False)
        else:
            st.warning(f"Unsupported file type: {file_extension}")
    except Exception as e:
        st.error(f"Error reading {file_extension.upper()} file: {e}")

    return content

def generate_business_requirement(input_text):
    """
    Generates business requirements using OpenAI's GPT model.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Ensure the model name is correct and accessible
            messages=[
                {"role": "system", "content": get_business_requirement_system_prompt()},
                {"role": "user", "content": get_business_requirement_user_prompt(input_text)}
            ],
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating business requirement: {str(e)}")
        return None

def create_copy_button(button_id):
    """
    Creates an HTML button with a given ID and styling for copying content.
    """
    return f"""
    <button id="{button_id}" style="{get_copy_button_style()}">
        <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#5F6368" style="margin-right: 4px;">
            <path d="M0 0h24v24H0z" fill="none"/>
            <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
        </svg>
        Copy
    </button>
    """

def create_copy_script(button_id, content_id):
    """
    Creates an embedded JavaScript script to handle the copy functionality.
    """
    return f"""
    <script>
    const copyButton_{button_id} = document.getElementById('{button_id}');
    const content_{content_id} = document.getElementById('{content_id}');

    copyButton_{button_id}.addEventListener('click', () => {{
        const textToCopy = content_{content_id}.innerText;
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
                alert('Failed to copy text.');
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
                alert('Failed to copy text.');
            }}
            document.body.removeChild(textArea);
        }}
    }});
    </script>
    """

def main():
    # Sidebar: File upload
    st.sidebar.subheader("Upload Document", divider="rainbow")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file",
        type=['txt', 'pdf', 'docx', 'xlsx', 'xls']
    )

    # Initialize session state for input text
    if 'input_text' not in st.session_state:
        st.session_state['input_text'] = ""

    # If a file is uploaded, read its content and load into the text area before widget creation
    if uploaded_file is not None:
        file_content = read_file_content(uploaded_file)
        if file_content:
            st.session_state['input_text'] = file_content  # Load file content into the text area

    # Text Area for Input (file content loaded here or manual input)
    input_text = st.text_area(
        "Enter or edit your business requirements here:",
        value=st.session_state['input_text'],
        height=300,
        key="input_text",
        help="You can upload a file or manually enter/edit your business requirements."
    )

    # Layout: Process button and copy button side by side
    col1, col2 = st.columns([3, 1])

    with col1:
        process_button = st.button("🔄 Process Requirement")

    with col2:
        # Embed a copy button via HTML for Input Content
        copy_button_html = f"""
        <button onclick="copyInputText()" style="{get_copy_button_style()}">
            <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 0 24 24" width="18px" fill="#5F6368" style="margin-right: 4px;">
                <path d="M0 0h24v24H0z" fill="none"/>
                <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
            </svg>
            Copy Input
        </button>
        <script>
        function copyInputText() {{
            // Select the text area by its unique key
            const textArea = document.querySelector('textarea[data-baseweb="textarea"]');
            if(textArea) {{
                textArea.select();
                textArea.setSelectionRange(0, 99999); // For mobile devices
                navigator.clipboard.writeText(textArea.value).then(() => {{
                    alert('Input content copied to clipboard!');
                }}).catch(err => {{
                    console.error('Failed to copy: ', err);
                    alert('Failed to copy text.');
                }});
            }} else {{
                alert('Text area not found!');
            }}
        }}
        </script>
        """
        components.html(copy_button_html, height=50)

    if process_button:
        with st.spinner("Processing..."):
            if st.session_state['input_text'].strip():
                business_requirement = generate_business_requirement(st.session_state['input_text'])
                if not business_requirement:
                    st.error("Failed to generate business requirement. Please try again.")
            else:
                st.warning("Please upload a file or enter text before processing.")

    # Display Business Requirement with Copy Button
    if 'business_requirement' in locals() and business_requirement:
        # Convert business_requirement markdown to HTML with extensions for better formatting
        requirement_html_content = markdown.markdown(business_requirement, extensions=['tables', 'fenced_code'])

        # Create unique IDs
        copy_button_id = "copy-requirement-button"
        content_id = "requirement-content"

        # HTML content with copy button and script
        requirement_html = f"""
        <div style="{get_content_container_style()}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; color: #202124;">Business Requirement</h4>
                {create_copy_button(copy_button_id)}
            </div>
        </div>
        <div id="{content_id}" style="{get_content_style()}">
            {requirement_html_content}
        </div>
        {create_copy_script(copy_button_id, content_id)}
        """

        # Render the HTML content with embedded JavaScript
        components.html(requirement_html, height=600, scrolling=True)
    else:
        if process_button:
            st.info("Translated business requirement will appear here after processing.")

if __name__ == "__main__":
    main()
