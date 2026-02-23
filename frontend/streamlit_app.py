import streamlit as st
import requests
import json

st.set_page_config(page_title="AI Support Desk", layout="centered")
st.title("AI Support Desk with Knowledge Routing")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Ask me anything about support, orders, or FAQs..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"messages": st.session_state.messages},
            timeout=30
        )

        for chunk in response.iter_content(decode_unicode=True):
            if chunk:
                full_response += chunk
                message_placeholder.write(full_response + "▌")

        message_placeholder.write(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})