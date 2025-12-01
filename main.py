import streamlit as st
import pandas as pd
import datetime
from datetime import date, timedelta
import google.generativeai as genai
import plotly.graph_objects as go
import time
import json
import os

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Project Zero Two", page_icon="logo.jpg", layout="wide")

# --- 2. GLOBAL THEME ENGINE (FIXED SCOPE) ---
# This runs immediately to ensure variables exist for graphs
if 'theme_choice' not in st.session_state:
    st.session_state['theme_choice'] = "Zero Two (Dark)"

def get_theme_vars(theme_name):
    if theme_name == "Zero Two (Dark)":
        return {
            "bg": "#050505", "text": "#e0e0e0", "accent": "#ff003c",
            "graph_temp": "plotly_dark", "graph_text": "white", "graph_line": "#ff003c"
        }
    else:
        return {
            "bg": "#ffffff", "text": "#111111", "accent": "#0984e3",
            "graph_temp": "plotly_white", "graph_text": "black", "graph_line": "#0984e3"
        }

theme = get_theme_vars(st.session_state['theme_choice'])

# Apply CSS
st.markdown(f"""
<style>
    .stApp {{ background-color: {theme['bg']}; color: {theme['text']}; }}
    h1, h2, h3 {{ 
        background: -webkit-linear-gradient(0deg, {theme['accent']}, #888);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-family: 'Helvetica Neue', sans-serif; font-weight: 800;
    }}
    div[data-testid="stMetricValue"] {{ color: {theme['accent']}; }}
    .stButton>button {{ color: {theme['accent']}; border: 1px solid {theme['accent']}; background: transparent; }}
    div[data-testid="stContainer"] {{ border: 1px solid #333; background-color: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; }}
    /* Custom Checkbox Style */
    .stCheckbox label {{ color: {theme['text']}; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

# --- 3. MASTER DATA ---
def get_syllabus_data(exam_type):
    # ACCURATE SYLLABUS LIST
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

def get_subject_breakdown(df):
    data = {}
    for sub in ["Physics", "Chemistry", "Maths"]:
        sub_df = df[df['Subject'] == sub]
        if not sub_df.empty:
            w = sub_df['Weightage'].map({"High":3, "Avg":2, "Low":1}).sum()
            e = sub_df['Impact_Score'].sum()
            data[sub] = int((e/w)*100) if w > 0 else 0
    return data

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f: return json.load(f)
    return None

def save_profile(target, df_data, daily_tasks=None, history=None, mistakes=None):
    if history is None:
        existing = load_profile()
        history = existing.get('history', []) if existing else []
    if mistakes is None:
        existing = load_profile()
        mistakes = existing.get('mistakes', []) if existing else []
    if daily_tasks is None:
        existing = load_profile()
        daily_tasks = existing.get('daily_tasks', []) if existing else []
        
    data = {
        "target": target, 
        "syllabus_data": df_data.to_dict('records'), 
        "history": history,
        "mistakes": mistakes,
        "daily_tasks": daily_tasks,
        "setup_complete": True
    }
    with open(PROFILE_FILE, 'w') as f: json.dump(data, f)
    return data

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
    # NEW: Manual Tasks List
    if 'daily_tasks' not in st.session_state:
        st.session_state['daily_tasks'] = profile.get('daily_tasks', [])
    
    readiness, est_score, target_marks = calculate_metrics(df, target)
    sub_breakdown = get_subject_breakdown(df)
    
    today_str = str(date.today())
    if not history or history[-1]['date'] != today_str:
        history.append({"date": today_str, "score": readiness})
        save_profile(target, df, st.session_state['daily_tasks'], history, mistakes)

    # SIDEBAR
    with st.sidebar:
        st.title("PROJECT 02")
        
        # THEME TOGGLE (Updates Session State -> Triggers Rerun)
        new_theme = st.radio("Theme", ["Zero Two (Dark)", "EdTech (Light)"], index=0 if st.session_state['theme_choice'] == "Zero Two (Dark)" else 1)
        if new_theme != st.session_state['theme_choice']:
            st.session_state['theme_choice'] = new_theme
            st.rerun()
            
        st.divider()
        if st.button("Reset App (Delete Data)"):
            os.remove(PROFILE_FILE)
            st.session_state['user_profile'] = None
            st.rerun()

    # TABS
    tab_home, tab_analytics, tab_syll, tab_mistakes, tab_ai = st.tabs(
        ["🏠 HOME", "📊 ANALYTICS", "📝 SYLLABUS", "🩸 MISTAKE AUTOPSY", "💬 ZERO TWO"]
    )

    # TAB 1: HOME (Manual Goals)
    with tab_home:
        with st.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("Readiness", f"{readiness}%", "Weighted")
            c2.metric("Est. Score", f"{est_score}", f"Target: {target_marks}")
            c3.metric("System", "Online" if api_status else "Offline")
        
        st.divider()
        
        # MANUAL MISSION CONTROL
        st.subheader("📝 Mission Control (Daily Targets)")
        
        c_add, c_list = st.columns([1, 2])
        
        with c_add:
            new_task = st.text_input("New Task", placeholder="Ex: Solve 20 Physics PYQs")
            if st.button("Add Mission"):
                if new_task:
                    st.session_state['daily_tasks'].append({"task": new_task, "done": False})
                    save_profile(target, df, st.session_state['daily_tasks'], history, mistakes)
                    st.rerun()
        
        with c_list:
            if st.session_state['daily_tasks']:
                for i, t in enumerate(st.session_state['daily_tasks']):
                    col_chk, col_del = st.columns([8, 1])
                    with col_chk:
                        # Checkbox updates state
                        is_done = st.checkbox(t['task'], value=t['done'], key=f"task_{i}")
                        if is_done != t['done']:
                            st.session_state['daily_tasks'][i]['done'] = is_done
                            save_profile(target, df, st.session_state['daily_tasks'], history, mistakes)
                            st.rerun()
                    with col_del:
                        if st.button("✖", key=f"del_{i}"):
                            st.session_state['daily_tasks'].pop(i)
                            save_profile(target, df, st.session_state['daily_tasks'], history, mistakes)
                            st.rerun()
                
                # Progress Bar for tasks
                done_count = sum(1 for t in st.session_state['daily_tasks'] if t['done'])
                total_count = len(st.session_state['daily_tasks'])
                if total_count > 0:
                    st.progress(done_count / total_count)
                    st.caption(f"{done_count}/{total_count} Missions Complete")
            else:
                st.info("No active missions. Add one to begin.")

    # TAB 2: ANALYTICS (Graphs with Global Colors)
    with tab_analytics:
        st.subheader("🚀 Goal Analysis")
        c1, c2 = st.columns([2, 1])
        with c1:
            fig_gap = go.Figure()
            fig_gap.add_trace(go.Bar(y=['Score'], x=[est_score], name='You', orientation='h', marker_color=theme['accent']))
            fig_gap.add_trace(go.Bar(y=['Score'], x=[target_marks], name='Target', orientation='h', marker_color='#888', opacity=0.5))
            fig_gap.update_layout(template=theme['graph_temp'], barmode='overlay', height=200, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=theme['graph_text']))
            st.plotly_chart(fig_gap, use_container_width=True)
        with c2:
            st.warning(f"GAP: {target_marks - est_score} Marks")
            
        st.divider()
        st.subheader("🧠 Subject Breakdown")
        cp1, cp2, cp3 = st.columns(3)
        def donut(val, color):
            v_done = val if val > 0 else 0
            return go.Figure(data=[go.Pie(values=[v_done, 100-v_done], hole=.6, marker_colors=[color, '#333' if 'dark' in theme['graph_temp'] else '#eee'])]).update_layout(showlegend=False, height=150, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)', font=dict(color=theme['graph_text']))
        
        with cp1: st.markdown("**Physics**"); st.plotly_chart(donut(sub_breakdown.get("Physics",0), "#007CF0"), use_container_width=True)
        with cp2: st.markdown("**Chemistry**"); st.plotly_chart(donut(sub_breakdown.get("Chemistry",0), "#00DFD8"), use_container_width=True)
        with cp3: st.markdown("**Maths**"); st.plotly_chart(donut(sub_breakdown.get("Maths",0), "#ff003c"), use_container_width=True)

        st.divider()
        st.subheader("📈 Consistency Tracker")
        if history:
            h_df = pd.DataFrame(history)
            fig_line = go.Figure(go.Scatter(x=h_df['date'], y=h_df['score'], mode='lines+markers', line=dict(color=theme['graph_line'])))
            fig_line.update_layout(template=theme['graph_temp'], height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=theme['graph_text']))
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
            save_profile(target, df, st.session_state['daily_tasks'], history, mistakes)
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

    # TAB 4: MISTAKE AUTOPSY
    with tab_mistakes:
        st.subheader("🩸 Error Autopsy")
        with st.expander("Log New Mistake"):
            m_sub = st.selectbox("Subject", ["Physics", "Chemistry", "Maths"], key="m_sub")
            m_topic = st.text_input("Topic/Chapter")
            m_type = st.selectbox("Error Type", ["Conceptual", "Silly", "Calculation", "Time Mgmt"])
            m_note = st.text_area("What went wrong?")
            if st.button("Log Error"):
                mistakes.append({"date": str(date.today()), "subject": m_sub, "topic": m_topic, "type": m_type, "note": m_note})
                save_profile(target, df, st.session_state['daily_tasks'], history, mistakes)
                st.rerun()
        
        if mistakes:
            m_df = pd.DataFrame(mistakes)
            st.dataframe(m_df, use_container_width=True)
            err_counts = m_df['type'].value_counts()
            fig_err = go.Figure(data=[go.Pie(labels=err_counts.index, values=err_counts.values, hole=.5)])
            fig_err.update_layout(template=theme['graph_temp'], height=250, paper_bgcolor='rgba(0,0,0,0)', font=dict(color=theme['graph_text']))
            st.plotly_chart(fig_err, use_container_width=True)
        else:
            st.info("No mistakes logged yet.")

    # TAB 5: MENTOR (Zero Two Aware)
    with tab_ai:
        st.subheader("💬 Zero Two")
        q = st.chat_input("Ask strategy...")
        if q and api_status:
            with st.chat_message("user"): st.write(q)
            with st.chat_message("assistant"):
                # Enhanced Context for AI
                context = f"""
                User Status:
                - Exam Goal: {target}
                - Readiness Score: {readiness}%
                - Weakest Subject: {min(sub_breakdown, key=sub_breakdown.get)} ({min(sub_breakdown.values())}%)
                - Recent Mistakes: {len(mistakes)} logged.
                """
                try:
                    res = model.generate_content(f"Act as academic strategist Zero Two. {context}. User: {q}")
                    st.write(res.text)
                except: st.error("AI Error")
