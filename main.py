import os
import base64
import streamlit as st
import streamlit.components.v1 as components

from utils.custom_css_main_page import get_main_custom_css
from utils.custom_css_banner import get_main_banner

# Set page config
st.set_page_config(page_title="💡 D&T Copilot", page_icon="🚀", layout="wide")

# Apply custom CSS
st.markdown(get_main_custom_css(), unsafe_allow_html=True)

# Function to encode an image file as base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

# Define create_agent_card function
def create_agent_card(col, image_path, title, description, page_link):
    encoded_image = encode_image(image_path)
    
    col.markdown(f"""
    <div class="agent-card">
        <div class="agent-content">
            <img src="data:image/png;base64,{encoded_image}" class="agent-icon">
            <div class="agent-title">{title}</div>
            <div class="agent-description">{description}</div>
        </div>
        <div class="agent-button">
            <!-- Button will be inserted here -->
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add Streamlit page link
    with col:
        button_container = st.container()
        with button_container:
            if st.button("Use", key=f"button_{title.replace(' ', '_').lower()}", use_container_width=True):
                st.switch_page(page_link)

# Main content
# Display the main banner
st.markdown(get_main_banner(), unsafe_allow_html=True)

# Create a list of agent cards
agents = [
    {
        "image": "meeting_summary_icon.png",
        "title": "📝 Meeting Summarization",
        "description": "Automatically summarize meetings and extract action items.",
        "page_link": "pages/1_📝_Meeting_Summary.py"
    },
    {
        "image": "requirement_translator_icon.png",
        "title": "🔄 Requirement Translator",
        "description": "Convert business requirements into technical specifications.",
        "page_link": "pages/2_🔄_Requirement_Translator.py"
    },
    {
        "image": "code_assistant_icon.png",
        "title": "💻 Code Assistant",
        "description": "Get AI-powered coding help and suggestions.",
        "page_link": "pages/3_💻_Coding_Assistant.py"
    }
]

# Display agent cards in a single row
cols = st.columns(3)
for i, agent in enumerate(agents):
    create_agent_card(
        cols[i],
        os.path.join(os.path.dirname(__file__), "image", agent["image"]),
        agent["title"],
        agent["description"],
        agent["page_link"]
    )
