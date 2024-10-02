import streamlit as st
import openai
import warnings
import base64
import io

from utils.message_utils import message_func
from utils.openai_utils import generate_response
from utils.custom_css_banner import get_code_assistant_banner
from openai import OpenAI

# Display the custom banner in the UI
st.markdown(get_code_assistant_banner(), unsafe_allow_html=True)

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set assistant ID (customized assistant)
# assistant_id = "asst_B4FNFJXuQhRegez9HXM6GPVz"
assistant_id = "asst_xPItAapKJu36iVy0D9AwdOZ7" # general assistant

warnings.filterwarnings("ignore")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi there! I'm your Code Assistant. How can I assist you today?"}
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
for message in st.session_state["messages"]:
    is_user = message["role"] == "user"
    message_func(message["content"], user_icon_base64, assistant_icon_base64, is_user=is_user)

# Accept user input
prompt = st.chat_input("Your message")

# File uploader for users to attach files
st.sidebar.subheader("Upload Document", divider="rainbow")
uploaded_file = st.sidebar.file_uploader("Attach a file")

# Handle user input and file upload
if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    message_func(prompt, user_icon_base64, assistant_icon_base64, is_user=True)

    # If a file is uploaded, pass it to the Code Interpreter and File Search
    file_id = None
    
    # File upload and handling
    if uploaded_file is not None:
        try:
            # Optionally read the file content
            # file_content = uploaded_file.read()

            # Reset the file pointer to the beginning
            uploaded_file.seek(0)

            # Upload the file including the filename
            file = client.files.create(
                file=uploaded_file,
                purpose="assistants"
            )
            file_id = file.id
            st.sidebar.success(f"File uploaded successfully with file_id: {file_id}")
        except Exception as e:
            st.sidebar.error(f"Failed to upload file: {str(e)}")


    # Generate a response using the assistant and pass the file if available
    response = generate_response(prompt, assistant_id, file_id)
    st.session_state["messages"].append({"role": "assistant", "content": response})
    message_func(response, user_icon_base64, assistant_icon_base64)


