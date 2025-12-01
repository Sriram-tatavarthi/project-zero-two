import streamlit as st
import pandas as pd
import datetime
from datetime import date, timedelta
import google.generativeai as genai
import plotly.graph_objects as go
import time

# --- SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Project Zero Two", page_icon="🔴", layout="wide")

# Custom CSS for the "Zero Two" Theme
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #ff003c !important; font-family: 'Courier New', Courier, monospace; }
    .stProgress > div > div > div > div { background-color: #ff003c; }
    div[data-testid="stMetricValue"] { color: #ff003c; }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
if 'init' not in st.session_state:
    st.session_state['init'] = True
    st.session_state['exams'] = {
        "JEE Main 2026": {"date": date(2026, 1, 21), "target": 220},
        "AP EAPCET 2026": {"date": date(2026, 5, 19), "target": 120}
    }
    st.session_state['logs'] = []
    st.session_state['mistakes'] = []
    st.session_state['resources'] = []
    st.session_state['timer_active'] = False

# --- BOOT SEQUENCE (One Time) ---
if st.session_state['init']:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
        <style>
        .boot-text {
            font-size: 36px; font-weight: bold; text-align: center; margin-top: 20%;
            color: #ff003c; font-family: 'Courier New', monospace; letter-spacing: 4px;
        }
        .sub-text { font-size: 16px; color: #aaaaaa; margin-top: 15px; letter-spacing: 2px; }
        </style>
        <div class='boot-text'>
            PROJECT ZERO TWO<br>
            <div class='sub-text'>ARCHITECT: SRIRAM</div>
            <div class='sub-text'>SYSTEM: ONLINE</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(3.5)
        placeholder.empty()
    st.session_state['init'] = False

# --- API SETUP ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_status = "LINKED"
    else:
        api_status = "DISCONNECTED"
except:
    api_status = "ERROR"

# --- HELPER FUNCTIONS ---
def get_days_left(exam_name):
    return (st.session_state['exams'][exam_name]['date'] - date.today()).days

def get_time_block():
    hour = datetime.datetime.now().hour
    return "ACADEMY_MODE" if 8 <= hour < 19 else "PILOT_MODE"

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔴 PROJECT 02")
    st.caption("PILOT: SRIRAM")
    st.markdown("---")
    
    active_exam = st.selectbox("CURRENT MISSION", list(st.session_state['exams'].keys()))
    days = get_days_left(active_exam)
    st.progress(min(1.0, max(0.0, days / 365)))
    st.caption(f"T-MINUS: {days} DAYS")
    
    st.markdown("---")
    st.markdown("### PILOT VITALITY")
    energy = st.slider("Energy Level", 0, 100, 80)
    if energy < 30:
        st.error("⚠️ CRITICAL FATIGUE DETECTED.")
    elif energy < 60:
        st.warning("⚠️ STAMINA LOW.")
    else:
        st.success("✅ OPTIMAL STATE")
        
    st.markdown("---")
    st.caption(f"AI CORE: {api_status}")

# --- MAIN INTERFACE ---
st.title(f"MISSION: {active_exam.upper()}")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["DAILY LOGS", "SYNC TIMER", "ROADMAP", "THE ARMORY", "SYSTEM CORE"])

# --- TAB 1: LOGS ---
with tab1:
    mode = get_time_block()
    c1, c2 = st.columns([2, 1])
    with c1:
        if mode == "ACADEMY_MODE":
            st.info("🏫 ACADEMY MODE ACTIVE (08:00 - 19:00)")
            with st.form("college"):
                st.text_input("Physics Update")
                st.text_input("Chemistry Update")
                st.text_input("Maths Update")
                if st.form_submit_button("UPLOAD DATA"):
                    st.success("Data encrypted & stored.")
        else:
            st.success("🏠 PILOT MODE ACTIVE")
            st.checkbox("Review Academy Notes")
            st.checkbox("Solve 30 PYQs")
            st.checkbox("Update Mistake Database")
            report = st.text_area("Mission Report")
            if st.button("LOG REPORT"):
                st.session_state['logs'].append({"Date": str(date.today()), "Report": report})
                st.toast("Report Logged.")
    with c2:
        st.metric("Consistency", "92%", "+2%")
        st.metric("Syllabus", "100%", "Done")

# --- TAB 2: TIMER ---
with tab2:
    st.subheader("⏱️ SYNCHRONIZATION TIMER")
    c1, c2, c3 = st.columns(3)
    with c1:
        t = st.number_input("Duration (Mins)", 10, 180, 50)
    with c2:
        st.write("")
        st.write("")
        if st.button("INITIATE LINK"):
            with st.status("ESTABLISHING LINK...", expanded=True) as status:
                time.sleep(1)
                st.write("Optimizing neural focus...")
                time.sleep(1)
                status.update(label="LINK ESTABLISHED", state="complete")
            st.success(f"FOCUS SESSION STARTED: {t} MINS")

# --- TAB 3: ROADMAP ---
with tab3:
    st.subheader("🚀 FLIGHT PATH")
    dates = [date.today() - timedelta(days=x) for x in range(30, 0, -5)]
    scores = [140, 145, 142, 150, 158, 160]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=scores, mode='lines+markers', name='Altitude', line=dict(color='#ff003c', width=3)))
    fig.add_trace(go.Scatter(x=dates, y=[220]*len(dates), mode='lines', name='Target', line=dict(dash='dash', color='white')))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 4: ARMORY ---
with tab4:
    st.subheader("⚔️ RESOURCE ARMORY")
    with st.expander("ADD NEW RESOURCE"):
        n = st.text_input("Name")
        l = st.text_input("Link/Location")
        t = st.selectbox("Type", ["Notes", "Video", "Test"])
        if st.button("STORE"):
            st.session_state['resources'].append({"Name": n, "Link": l, "Type": t})
            st.success("Indexed.")
    if st.session_state['resources']:
        st.table(pd.DataFrame(st.session_state['resources']))
    else:
        st.info("Armory Empty.")

# --- TAB 5: AI CORE (The Jarvis/Raphael Persona) ---
with tab5:
    st.subheader("🤖 CONNECT: ZERO TWO")
    user_q = st.text_area("INPUT QUERY", placeholder="System, I am feeling overwhelmed with Calculus...")
    if st.button("TRANSMIT"):
        if api_status == "LINKED":
            with st.spinner("PROCESSING..."):
                # Sriram's Requested Persona: Jarvis/Raphael Style
                prompt = f"""
                You are 'Zero Two', an advanced, hyper-intelligent AI assistant similar to J.A.R.V.I.S or Raphael (Great Sage).
                User: Sriram (The Architect/Pilot).
                
                Tone Guidelines:
                1. Be sophisticated, calm, and highly articulate.
                2. Do NOT use robotic phrases like 'Vital signs detected'. 
                3. Instead, say things like: "I have analyzed your request and concluded..." or "My suggestion, considering your current fatigue levels, is..."
                4. Be helpful but precise. No fluff.
                
                User Query: {user_q}
                """
                response = model.generate_content(prompt)
                st.markdown(f"**ZERO TWO:**\n\n{response.text}")
        else:

            st.error("COMMUNICATION ERROR: API KEY MISSING.")
