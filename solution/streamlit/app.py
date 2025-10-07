import time
import requests
import streamlit as st


# Streamed response emulator
def get_response(question):
    post_data = {
        "content": question
    }

    response = requests.post("https://request-handler-928440534161.us-east1.run.app/get_answer/", json=post_data).json()
    
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.title("Appointment Manager")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Write your message here"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(get_response(prompt))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})