import streamlit as st
import openai
import warnings
import base64
from openai import OpenAI

from utils.message_utils import message_func
from utils.openai_utils import generate_response


# Import your custom CSS functions
from utils.custom_css_banner import get_code_assistant_banner

st.markdown(get_code_assistant_banner(), unsafe_allow_html=True)

# Initialize OpenAI API Key (ensure you have this in your environment or secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Set assistant id 
assistant_id = "asst_B4FNFJXuQhRegez9HXM6GPVz" # openai-customed-code-assistant-id


warnings.filterwarnings("ignore")
chat_history = []

# Model selection radio button
model = "gpt-4o-mini"
st.session_state["model"] = model

# Load icons for user and assistant
def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"

# Load icons for user and assistant
user_icon_path = "image/user_icon.png"
assistant_icon_path = "image/assistant_icon.png"

user_icon_base64 = get_image_base64(user_icon_path)
assistant_icon_base64 = get_image_base64(assistant_icon_path)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi there! I'm your D&T Code Assistant, here to help you streamline your software development process. Whether you need assistance with coding, security, testing, or documentation, I'm ready to assist. What can I help you with today?"}
    ]


# Display chat messages
for message in st.session_state["messages"]:
    is_user = message["role"] == "user"
    message_func(message["content"], user_icon_base64, assistant_icon_base64, is_user=is_user, model=model)



# Accept user input and generate a response
prompt = st.chat_input("Your message")
if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    message_func(prompt, user_icon_base64, assistant_icon_base64, is_user=True, model=model)

    response = generate_response(prompt, assistant_id)
    st.session_state["messages"].append({"role": "assistant", "content": response})
    message_func(response, user_icon_base64, assistant_icon_base64, model=model)

