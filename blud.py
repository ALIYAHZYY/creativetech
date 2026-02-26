import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from streamlit_calendar import calendar
from datetime import datetime

# -------------------------------
# Firebase Initialization (Fixed Safe Version)
# -------------------------------cd
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="Upgraded Notes App", layout="wide")
st.title("📝 Smart Note Application")

# -------------------------------
# Sidebar Navigation
# -------------------------------
menu = st.sidebar.selectbox(
    "Navigation",
    ["Notes", "To-Do List", "Events"]
)

# ===============================
# NOTES SECTION (NOW WITH DATE)
# ===============================
if menu == "Notes":
    st.header("📒 Notes")

    note_title = st.text_input("Note Title")
    note_content = st.text_area("Write your note")
    note_date = st.date_input("Select Note Date")

    if st.button("Add Note"):
        db.collection("notes").add({
            "title": note_title,
            "content": note_content,
            "date": note_date.isoformat(),
            "timestamp": datetime.now()
        })
        st.success("Note Added!")
        st.rerun()

    st.subheader("Saved Notes")
    notes = db.collection("notes").stream()

    for note in notes:
        data = note.to_dict()
        st.write(f"### {data['title']}")
        st.write(f"📅 {data.get('date', 'No Date')}")
        st.write(data['content'])

        if st.button("Delete", key=note.id):
            db.collection("notes").document(note.id).delete()
            st.warning("Note Deleted!")
            st.rerun()

# ===============================
# TODO SECTION
# ===============================
elif menu == "To-Do List":
    st.header("✅ To-Do List")

    task = st.text_input("New Task")

    if st.button("Add Task"):
        db.collection("tasks").add({
            "task": task,
            "done": False,
            "date": datetime.now().date().isoformat()
        })
        st.success("Task Added!")
        st.rerun()

    tasks = db.collection("tasks").stream()

    for t in tasks:
        data = t.to_dict()
        col1, col2 = st.columns([4,1])

        col1.write(data["task"])

        if col2.button("❌", key=t.id):
            db.collection("tasks").document(t.id).delete()
            st.rerun()

# ===============================
# EVENTS SECTION (CALENDAR INSIDE)
# ===============================
elif menu == "Events":
    st.header("📅 Events")

    event_name = st.text_input("Event Name")
    event_date = st.date_input("Event Date")

    if st.button("Add Event"):
        db.collection("events").add({
            "title": event_name,
            "date": event_date.isoformat()
        })
        st.success("Event Added!")
        st.rerun()

    st.subheader("Event List")

    events_data = []
    events = db.collection("events").stream()

    for e in events:
        data = e.to_dict()

        st.write(f"📌 {data['title']} - {data['date']}")

        events_data.append({
            "title": data["title"],
            "start": data["date"]
        })

        if st.button("Delete Event", key=e.id):
            db.collection("events").document(e.id).delete()
            st.rerun()

    # -------- CALENDAR DISPLAY --------
    st.subheader("📆 Calendar View")
    calendar(events=events_data)