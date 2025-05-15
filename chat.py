import streamlit as st
import csv
import os
import hashlib
from datetime import datetime

# File paths
USERS_FILE = 'users.csv'
MESSAGES_FILE = 'messages.csv'

# Initialize files
def init_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password'])
    
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['sender', 'message', 'timestamp'])

init_files()

def create_user(username, password):
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    with open(USERS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([username, hashed_pw])

def verify_user(username, password):
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    with open(USERS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] == username and row['password'] == hashed_pw:
                return True
    return False

def add_message(sender, message):
    timestamp = datetime.now().isoformat()
    with open(MESSAGES_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([sender, message, timestamp])

def get_messages():
    messages = []
    with open(MESSAGES_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            messages.append(row)
    return messages

# ------------------ NEW ADDITIONS ------------------
def login_page():
    st.title("Private Chat Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if verify_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid credentials")
    
    if st.button("Register"):
        if username and password:
            create_user(username, password)
            st.success("Registered successfully! Please login")
        else:
            st.error("Please fill both fields")

def chat_page():
    st.title(f"Private Chat - Welcome {st.session_state.username}")
    messages = get_messages()
    
    for msg in reversed(messages):  # Show latest messages at bottom
        st.write(f"**{msg['sender']}** ({msg['timestamp'][:16]}): {msg['message']}")
    
    new_message = st.text_input("Type your message", key="new_msg")
    if st.button("Send"):
        if new_message:
            add_message(st.session_state.username, new_message)
            st.rerun()

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        chat_page()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    main()