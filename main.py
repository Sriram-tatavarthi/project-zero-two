import streamlit as st
import pandas as pd
import datetime
from datetime import date, timedelta
import google.generativeai as genai
import plotly.graph_objects as go
import time
import json
import os
import pypdf

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Project Zero Two", page_icon="logo.jpg", layout="wide")

# --- 2. DYNAMIC THEME ENGINE ---
def apply_theme(theme_name):
    if theme_name == "Zero Two (Dark)":
        # VOID BLACK & NEON RED
        st.markdown("""
        <style>
            .stApp { background-color: #050505; color: #e0e0e0; }
            h1, h2, h3 { 
                background: -webkit-linear-gradient(0deg, #ff003c, #ff80ab);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-family: 'Helvetica Neue', sans-serif; font-weight: 800;
            }
            div[data-testid="stMetricValue"] { color: #ff003c; }
            .stButton>button { color: #ff003c; border: 1px solid #ff003c; background: #1a0b0e; }
            div[data-testid="stContainer"] { border: 1px solid #333; background-color: #0a0a0a; border-radius: 10px; padding: 15px; }
            .report-box { border-left: 4px solid #ff003c; background: rgba(255, 0, 60, 0.1); padding: 15px; }
        </style>
        """, unsafe_allow_html=True)
        return "dark"
    else:
        # EDTECH (Light) - CLEAN & VISIBLE
        st.markdown("""
        <style>
            .stApp { background-color: #ffffff; color: #111; }
            h1, h2, h3 { 
                background: -webkit-linear-gradient(0deg, #0984e3, #00cec9);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-family: 'Verdana', sans-serif; font-weight: 700;
            }
            div[data-testid="stMetricValue"] { color: #0984e3; }
            .stButton>button { color: white; border: none; background: linear-gradient(90deg, #0984e3, #00cec9); }
            div[data-testid="stContainer"] { border: 1px solid #e0e0e0; background-color: #f9f9f9; border-radius: 10px; padding: 15px; }
            .report-box { border-left: 4px solid #0984e3; background: rgba(9, 132, 227, 0.1); padding: 15px; }
        </style>
        """, unsafe_allow_html=True)
        return "light"

# --- 3. MASTER DATA ---
def get_syllabus_data(exam_type):
    syllabus = [
        {"Subject": "Physics", "Chapter": "Units & Dimensions", "Weightage": "Low"},
        {"Subject": "Physics", "Chapter": "Experimental Physics", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Kinematics", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Laws of Motion", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Work, Energy & Power", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Rotational Motion", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Gravitation", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Solids & Fluids", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Thermodynamics", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "SHM & Waves", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Electrostatics", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Current Electricity", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Magnetism", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "EMI & AC", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Optics", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Modern Physics", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Semiconductors", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Mole Concept", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Atomic Structure", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Chemical Bonding", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Thermodynamics", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Equilibrium", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Solutions", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Electrochemistry", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Kinetics", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Inorganic (Block Elements)", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Coordination Compounds", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "GOC", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Hydrocarbons", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Haloalkanes/Haloarenes", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Oxygen Compounds", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Nitrogen Compounds", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Biomolecules", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "POC & Titration", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Sets & Functions", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Complex Numbers", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Quadratic Eq", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Matrices & Det", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Permutations & Comb", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Binomial Theorem", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Sequence & Series", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Calculus (Diff)", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Calculus (Integral)", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Differential Eq", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Coordinate Geometry", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Vectors & 3D", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Probability", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Trigonometry", "Weightage": "Low"}
    ]
    if exam_type == "AP EAPCET 2026":
        extras = [
            {"Subject": "Chemistry", "Chapter": "Solid State", "Weightage": "Avg"},
            {"Subject": "Chemistry", "Chapter": "Polymers", "Weightage": "Low"},
            {"Subject": "Chemistry", "Chapter": "Everyday Life", "Weightage": "Low"}
        ]
        syllabus.extend(extras)
    return syllabus

PROFILE_FILE = "user_profile.json"

# --- 4. API & LOGIC ---
model = None
api_status = False

def init_ai():
    if "GEMINI_API_KEY" not in st.secrets: return None, False
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    candidates = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
    for m in candidates:
        try:
            test_model = genai.GenerativeModel(m)
            test_model.generate_content("test")
            return test_model, True
        except: continue
    return None, False

model, api_status = init_ai()

def calculate_metrics(df, target_exam):
    w_vals = {"High": 3, "Avg": 2, "Low": 1}
    df['W_Score'] = df['Weightage'].map(w_vals)
    df['Impact_Score'] = 0.0
    for i, row in df.iterrows():
        val = 0.0
        if row['Status'] == 'Mastered': val = 1.0
        elif row['Status'] == 'Revision 2': val = 0.8
        elif row['Status'] == 'Revision 1': val = 0.5
        df.at[i, 'Impact_Score'] = val * row['W_Score']
    total = df['W_Score'].sum()
    earned = df['Impact_Score'].sum()
    readiness = int((earned/total)*100) if total > 0 else 0
    
    total_marks = 300 if "JEE" in target_exam else 160
    target_marks = 240 if "JEE" in target_exam else 130
    est_score = int(total_marks * (readiness / 100))
    return readiness, est_score, target_marks

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f: return json.load(f)
    return None

def save_profile(target, df_data, schedule_text="", history=None, mistakes=None):
    if history is None:
        existing = load_profile()
        history = existing.get('history', []) if existing else []
    if mistakes is None:
        existing = load_profile()
        mistakes = existing.get('mistakes', []) if existing else []
        
    data = {
        "target": target, 
        "syllabus_data": df_data.to_dict('records'), 
        "history": history,
        "mistakes": mistakes,
        "schedule_text": schedule_text,
        "setup_complete": True
    }
    with open(PROFILE_FILE, 'w') as f: json.dump(data, f)
    return data

def ai_process_log(text, current_syllabus):
    valid_chaps = [x['Chapter'] for x in current_syllabus]
    prompt = f"Analyze: '{text}'. Match to: {valid_chaps}. Return valid JSON list: [{{'Chapter': 'Name', 'Status': 'Mastered'}}]"
    try:
        response = model.generate_content(prompt)
        clean = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except: return []

# --- 5. SMART PDF PARSER (FIXED FOR YOUR TABLE) ---
def parse_schedule_pdf(uploaded_file):
    try:
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages: text += page.extract_text()
        
        today = str(date.today())
        
        # SPECIFIC PROMPT FOR YOUR TABLE STRUCTURE
        prompt = f"""
        You are a Schedule Analyzer. 
        TODAY'S DATE: {today}
        
        DOCUMENT CONTENT: {text[:6000]}
        
        INSTRUCTIONS:
        1. Look for rows where the DATE column matches Today ({today}).
        2. Extract the TOPICS listed in Physics, Chemistry, and Maths columns for that date.
        3. Look for "WTM", "CTM", "PTM", or "Grand Test" in the next 7 days.
        
        OUTPUT FORMAT (Strictly):
        **Today's Targets:**
        * [Subject]: [Topic]
        * [Subject]: [Topic]
        
        **Battle Radar (Next 7 Days):**
        * [Date] - [Exam Name]
        """
        response = model.generate_content(prompt)
        return response.text
    except: return "Could not parse schedule. Ensure PDF is readable."

# --- 6. MAIN APPLICATION ---
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = load_profile()

if not st.session_state['user_profile']:
    # SETUP WIZARD
    st.title("🚀 SYSTEM INITIALIZATION")
    target_sel = st.selectbox("SELECT GOAL", ["JEE Main 2026", "JEE Advanced 2026", "AP EAPCET 2026"])
    if 'wizard_df' not in st.session_state:
        st.session_state['wizard_df'] = pd.DataFrame(get_syllabus_data(target_sel))
        st.session_state['wizard_df']['Status'] = 'Pending'
        st.session_state['wizard_df']['Confidence'] = 0
        st.session_state['wizard_df']['Impact_Score'] = 0.0
    
    st.info("Mark completed chapters.")
    edited_df = st.data_editor(st.session_state['wizard_df'], use_container_width=True, hide_index=True)
    if st.button("START DASHBOARD"):
        save_profile(target_sel, edited_df)
        st.session_state['user_profile'] = load_profile()
        st.rerun()

else:
    # LOAD DATA
    profile = st.session_state['user_profile']
    target = profile['target']
    df = pd.DataFrame(profile['syllabus_data'])
    history = profile.get('history', [])
    mistakes = profile.get('mistakes', [])
    schedule_text = profile.get('schedule_text', "No schedule uploaded.")
    
    readiness, est_score, target_marks = calculate_metrics(df, target)
    
    # Update History if changed
    today_str = str(date.today())
    if not history or history[-1]['date'] != today_str:
        history.append({"date": today_str, "score": readiness})
        save_profile(target, df, schedule_text, history, mistakes)

    # SIDEBAR
    with st.sidebar:
        st.title("PROJECT 02")
        theme_choice = st.radio("Theme", ["Zero Two (Dark)", "EdTech (Light)"])
        active_theme = apply_theme(theme_choice)
        
        st.divider()
        uploaded_file = st.file_uploader("Schedule PDF", type="pdf")
        if uploaded_file and api_status:
            if st.button("Scan PDF"):
                with st.spinner("Analyzing..."):
                    schedule_text = parse_schedule_pdf(uploaded_file)
                    save_profile(target, df, schedule_text, history, mistakes)
                    st.rerun()
        
        if st.button("Reset App"):
            os.remove(PROFILE_FILE)
            st.session_state['user_profile'] = None
            st.rerun()

    # TABS
    tab_home, tab_analytics, tab_syll, tab_mistakes, tab_ai = st.tabs(
        ["🏠 HOME", "📊 ANALYTICS", "📝 SYLLABUS", "🩸 MISTAKE BOOK", "💬 ZERO TWO"]
    )

    # TAB 1: HOME
    with tab_home:
        # Metrics
        with st.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("Readiness", f"{readiness}%", "Weighted")
            c2.metric("Est. Score", f"{est_score}", f"Target: {target_marks}")
            c3.metric("System", "Online" if api_status else "Offline")
        
        st.divider()
        
        # Schedule & Log
        c_sch, c_log = st.columns([1, 1])
        with c_sch:
            st.subheader("📅 Briefing")
            if "Battle" in schedule_text or "Exam" in schedule_text:
                st.error("⚠️ EXAM DETECTED")
            st.info(schedule_text)
            
        with c_log:
            st.subheader("⌨️ Quick Log")
            log_in = st.text_area("What did you finish today?", placeholder="I finished Electrostatics...")
            if st.button("Update Status"):
                if api_status:
                    ups = ai_process_log(log_in, profile['syllabus_data'])
                    if ups:
                        for u in ups:
                            df.loc[df['Chapter'].str.contains(u['Chapter'], case=False), 'Status'] = u['Status']
                        save_profile(target, df, schedule_text, history, mistakes)
                        st.success("Updated!")
                        st.rerun()

    # TAB 2: ANALYTICS (Graphs)
    with tab_analytics:
        st.subheader("🚀 Goal Analysis")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            # Goal Gap (Bar)
            fig_gap = go.Figure()
            fig_gap.add_trace(go.Bar(y=['Score'], x=[est_score], name='You', orientation='h', marker_color='#007CF0'))
            fig_gap.add_trace(go.Bar(y=['Score'], x=[target_marks], name='Target', orientation='h', marker_color='#00DFD8', opacity=0.5))
            text_col = "white" if active_theme == "dark" else "black"
            fig_gap.update_layout(barmode='overlay', height=200, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_col))
            st.plotly_chart(fig_gap, use_container_width=True)
            
        with c2:
            st.warning(f"GAP: {target_marks - est_score} Marks")
            
        st.divider()
        
        # Progress History (Line Chart)
        st.subheader("📈 Consistency Tracker")
        if history:
            h_df = pd.DataFrame(history)
            fig_line = go.Figure(go.Scatter(x=h_df['date'], y=h_df['score'], mode='lines+markers', line=dict(color='#ff003c')))
            fig_line.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_col))
            st.plotly_chart(fig_line, use_container_width=True)

    # TAB 3: SYLLABUS
    with tab_syll:
        st.subheader("🗂️ Master Codex")
        sub = st.selectbox("Subject", ["Physics", "Chemistry", "Maths"])
        ed_df = st.data_editor(
            df[df['Subject'] == sub], 
            use_container_width=True,
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Revision 1", "Revision 2", "Mastered"]),
                "Weightage": st.column_config.TextColumn("Impact", disabled=True),
                "Confidence": st.column_config.NumberColumn("Conf %", min_value=0, max_value=100)
            }
        )
        if st.button("Save Changes"):
            for i, r in ed_df.iterrows():
                mask = (df['Subject'] == r['Subject']) & (df['Chapter'] == r['Chapter'])
                df.loc[mask, 'Status'] = r['Status']
                df.loc[mask, 'Confidence'] = r['Confidence']
            save_profile(target, df, schedule_text, history, mistakes)
            st.success("Saved!")
            st.rerun()
            
        st.divider()
        if st.button("INITIALIZE DEEP AI SCAN"):
            if api_status:
                with st.spinner("Analyzing..."):
                    summary = df.groupby('Subject')['Status'].value_counts().to_json()
                    prompt = f"Analyze progress: {summary}. Goal: {target}. Give 3 strategic actions."
                    try:
                        report = model.generate_content(prompt).text
                        st.markdown(f"<div class='report-box'>{report}</div>", unsafe_allow_html=True)
                    except: st.error("AI Error")

    # TAB 4: MISTAKE BOOK (Replaced Library)
    with tab_mistakes:
        st.subheader("🩸 Error Autopsy")
        with st.expander("Log New Mistake"):
            m_sub = st.selectbox("Subject", ["Physics", "Chemistry", "Maths"], key="m_sub")
            m_topic = st.text_input("Topic/Chapter")
            m_type = st.selectbox("Error Type", ["Conceptual", "Silly", "Calculation", "Time Mgmt"])
            m_note = st.text_area("What went wrong?")
            if st.button("Log Error"):
                mistakes.append({"date": str(date.today()), "subject": m_sub, "topic": m_topic, "type": m_type, "note": m_note})
                save_profile(target, df, schedule_text, history, mistakes)
                st.rerun()
        
        if mistakes:
            m_df = pd.DataFrame(mistakes)
            st.dataframe(m_df, use_container_width=True)
            # Simple Chart
            err_counts = m_df['type'].value_counts()
            fig_err = go.Figure(data=[go.Pie(labels=err_counts.index, values=err_counts.values, hole=.5)])
            text_col = "white" if active_theme == "dark" else "black"
            fig_err.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', font=dict(color=text_col))
            st.plotly_chart(fig_err, use_container_width=True)
        else:
            st.info("No mistakes logged yet. Good job?")

    # TAB 5: MENTOR
    with tab_ai:
        st.subheader("💬 Zero Two")
        q = st.chat_input("Ask strategy...")
        if q and api_status:
            with st.chat_message("user"): st.write(q)
            with st.chat_message("assistant"):
                try:
                    res = model.generate_content(f"Act as academic strategist Zero Two. Goal: {target}. User: {q}")
                    st.write(res.text)
                except: st.error("AI Error")
