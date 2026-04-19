# capstone_streamlit.py

import streamlit as st
from agent import ask_agent

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Agentic AI Assistant", layout="wide")

st.title("🤖 Agentic AI Course Assistant")
st.write("Ask questions about the 13-day Agentic AI course")

# -----------------------------
# SESSION MEMORY
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------
# USER INPUT
# -----------------------------
user_input = st.text_input("Ask your question:")

if st.button("Submit"):
    if user_input:
        with st.spinner("Thinking..."):
            response = ask_agent(user_input)

        # Save history
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Agent", response))

# -----------------------------
# DISPLAY CHAT
# -----------------------------
st.subheader("Conversation")

for role, msg in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"**🧑 {role}:** {msg}")
    else:
        st.markdown(f"**🤖 {role}:** {msg}")