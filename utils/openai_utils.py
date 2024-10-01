import openai
import time
import streamlit as st

from openai import OpenAI

api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# function: wait on the run to complete
def wait_on_run(run, thread_id):
    while run.status == 'queued' or run.status == 'in_progress':
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        # time.sleep(4)
        # print(run.status)

# function: display the response
def display_thread_messages(messages):
    message_texts = []
    for thread_message in messages.data[::-1]:
        # Append the message content to the list
        message_texts.append(thread_message.content[0].text.value)
    # Join the list into a single string separated by newlines
    return "\n\n".join(message_texts)

def generate_response(user_message, assistant_id):
    if 'thread_id' not in st.session_state:
        # initiate a new thread if one does not exist in session state
        thread = client.beta.threads.create()
        st.session_state['thread_id'] = thread.id
        print(f"New thread created: {thread.id}")
    else:
        print(f"Using existing thread: {st.session_state['thread_id']}")
    thread_id = st.session_state['thread_id']

    try:
        # add user_message to the thread
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role='user',
            content=user_message)

        # run a thread using required assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id)

        with st.spinner("Elfie is responding..."):
            wait_on_run(run, thread_id)

        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order='asc',
            after=message.id)

        return display_thread_messages(messages)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "Error generating response. Please try again."