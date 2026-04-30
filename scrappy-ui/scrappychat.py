import streamlit as st
import requests
import os

API_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:9000/investigate")
HTTP_SESSION = requests.Session()

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Scrappy Market AI",
    layout="wide"
)

# -------------------------------
# HEADER (like your screenshot)
# -------------------------------
st.markdown("""
<div style="
    background-color:#F5E6D3;
    padding:15px;
    border-radius:10px;
    display:flex;
    justify-content:space-between;
    align-items:center;
">
    <div style="font-size:22px; font-weight:bold; color:#E67E22;">
        🤖 Scrappy Market Agentic AI Assistant
    </div>
    <div>
        <span style="margin-right:15px;">Welcome, Raheem!</span>
        <button style="
            background:#fff;
            border:1px solid #ccc;
            padding:5px 10px;
            border-radius:8px;
        ">Sign Out</button>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------
# INIT STATE
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# CHAT DISPLAY
# -------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------
# INPUT
# -------------------------------
user_input = st.chat_input("How can I help you?")

# -------------------------------
# HANDLE USER INPUT
# -------------------------------
if user_input:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    answer = "No response"
    confidence = 0
    query_used = {}

    # Call Orchestrator API
    with st.spinner("Analyzing..."):
        try:
            res = HTTP_SESSION.post(
                API_URL,
                json={"question": user_input},
            )
            data = res.json()
            print("API Response:", data)
            print("Confidence field:", data.get("confidence"))
            print("Type:", type(data.get("confidence")))
            answer = data.get("answer", "No response")
            confidence = data.get("confidence", 0)
            query_used = data.get("query", {})

        except Exception as e:
            answer = f"Error: {str(e)}"
            confidence = 0

    # -------------------------------
    # STREAM RESPONSE (typing effect)
    # -------------------------------
    def stream_response(text):
        for word in text.split():
            yield word + " "

    with st.chat_message("assistant"):
        response = st.write_stream(stream_response(answer))
        st.caption(f"Confidence: {round(confidence, 2)}")

        with st.expander("View Query Used"):
            sql_preview = query_used.get("sql", "")
            params = query_used.get("params", [])

            for param in params:
                sql_preview = sql_preview.replace("?", f"'{param}'", 1)

            st.code(sql_preview, language="sql")
        with st.expander("View Parameters Used"):
            st.code(str(query_used.get("payload", {})), language="json")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "confidence": confidence
    })
