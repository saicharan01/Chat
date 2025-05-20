import streamlit as st
import csv
import os
import hashlib
from datetime import datetime
import emoji
import streamlit.components.v1 as components

# File paths
USERS_FILE = 'users.csv'
MESSAGES_FILE = 'messages.csv'

# Initialize files
def init_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password'])
    
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['sender', 'message', 'timestamp'])

init_files()

# Authentication
def create_user(username, password):
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    with open(USERS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([username, hashed_pw])

def verify_user(username, password):
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] == username and row['password'] == hashed_pw:
                return True
    return False

# Messages
def add_message(sender, message):
    timestamp = datetime.now().isoformat()
    with open(MESSAGES_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([sender, message, timestamp])

def get_messages():
    messages = []
    with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            messages.append(row)
    return messages
def emoji_picker():
    emoji_aliases = [
        ":grinning_face:", ":face_with_tears_of_joy:", ":smiling_face_with_heart_eyes:",
        ":thumbs_up:", ":red_heart:", ":party_popper:", ":fire:",
        ":crying_face:", ":smiling_face_with_sunglasses:", ":thinking_face:",
        ":pouting_face:", ":raising_hands:"
    ]

    emoji_html = """
    <script>
    function insertEmoji(emoji) {
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set("emoji", emoji);
        window.location.href = currentUrl.href;
    }
    </script>
    <style>
    .emoji-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        background: #fff;
        padding: 1rem;
        border: 1px solid #ddd;
        max-height: 200px;
        overflow-y: auto;
        border-radius: 10px;
    }
    .emoji-grid span {
        font-size: 24px;
        cursor: pointer;
    }
    </style>
    <div class="emoji-grid">
    """

    for alias in emoji_aliases:
        emoji_char = emoji.emojize(alias, language='alias')
        emoji_html += f'<span onclick="insertEmoji(\'{emoji_char}\')">{emoji_char}</span>\n'

    emoji_html += "</div>"

    components.html(emoji_html, height=250)
    # Append emoji from URL query param if exists
    query_params = st.experimental_get_query_params()
    if "emoji" in query_params:
        selected_emoji = query_params["emoji"][0]
        if "new_msg" in st.session_state:
            st.session_state.new_msg += selected_emoji
        else:
            st.session_state.new_msg = selected_emoji
        st.experimental_set_query_params()


# CSS Styling
st.markdown("""
<style>
.chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding: 1rem;
    background-color: #ECE5DD;
    border-radius: 15px;
}
.chat-message {
    padding: 1rem;
    border-radius: 15px;
    margin: 0.5rem 0;
    max-width: 70%;
    word-wrap: break-word;
}
.user-message {
    background-color: #DCF8C6;
    margin-left: auto;
}
.other-message {
    background-color: #FFFFFF;
    margin-right: auto;
}
.timestamp {
    font-size: 0.75rem;
    color: #666;
    margin-top: 0.25rem;
    text-align: right;
}
.bottom-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: white;
    padding: 10px 5%;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Login UI
def login_page():
    st.title("💬 WhatsApp-like Chat Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
    with col2:
        if st.button("Register"):
            if username and password:
                create_user(username, password)
                st.success("Registered successfully! Please login")
            else:
                st.error("Please fill both fields")

# Chat UI
def chat_page():
    st.title(f"💬 Chat - {st.session_state.username}")
    st.markdown("---")

    # Chat Area
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        messages = get_messages()
        for msg in messages:
            dt = datetime.fromisoformat(msg['timestamp'])
            formatted_time = dt.strftime("%I:%M %p")
            sender_class = "user-message" if msg['sender'] == st.session_state.username else "other-message"
            sender_display = "You" if msg['sender'] == st.session_state.username else msg['sender']
            st.markdown(f"""
                <div class="chat-message {sender_class}"><div><strong>{sender_display}</strong></div>
                <div>{msg['message']}</div><div class="timestamp">{formatted_time}</div></div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Emoji toggle
    with st.expander("😊 Emoji Picker"):
        emoji_picker()
    if "new_msg" not in st.session_state:
        st.session_state.new_msg = ""

    # Fixed Input Area
    with st.container():
        st.markdown('<div class="bottom-bar">', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            new_message = st.text_input("Type a message", key="new_msg", placeholder="Type a message...")
        with col2:
            if st.button("🚀 Send"):
                if new_message:
                    parsed_message = emoji.emojize(new_message, language='alias')
                    add_message(st.session_state.username, parsed_message)
                    del st.session_state["new_msg"]
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# Main
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()
