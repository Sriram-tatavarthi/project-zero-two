import streamlit as st
import pandas as pd
import datetime
from datetime import date, timedelta
import google.generativeai as genai
import plotly.graph_objects as go
import plotly.express as px
import time
import pypdf
import json

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Project Zero Two", page_icon="🔴", layout="wide")

# --- 2. PROFESSIONAL ZERO TWO THEME (CSS) ---
st.markdown("""
<style>
    /* MAIN BACKGROUND - VOID BLACK */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 50%, #1a0b0e 0%, #050505 100%);
    }
    
    /* GRADIENT HEADERS (Pink to Red) */
    h1, h2, h3, h4 {
        background: -webkit-linear-gradient(0deg, #ff003c, #ff80ab);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        letter-spacing: 1px;
    }
    
    /* GLASSMORPHISM CARDS */
    div[data-testid="stExpander"], div[data-testid="stContainer"] {
        background: rgba(20, 20, 20, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 0, 60, 0.15); /* Zero Two Red Border */
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    
    /* METRICS & TEXT */
    div[data-testid="stMetricValue"] {
        color: #ff003c;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 10px rgba(255, 0, 60, 0.4);
    }
    div[data-testid="stMetricLabel"] { color: #aaaaaa; }
    
    /* PROGRESS BARS - NEON PINK */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #ff003c, #ff6b95);
        box-shadow: 0 0 10px rgba(255, 0, 60, 0.5);
    }
    
    /* BUTTONS */
    div.stButton > button {
        background-color: #1a0b0e;
        color: #ff003c;
        border: 1px solid #ff003c;
        border-radius: 8px;
    }
    div.stButton > button:hover {
        background-color: #ff003c;
        color: white;
        box-shadow: 0 0 15px rgba(255, 0, 60, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. MASTER DATA (FULL 90+ CHAPTERS) ---
# Hardcoded to ensure user has full list immediately
FULL_SYLLABUS = [
    # PHYSICS
    {"Subject": "Physics", "Chapter": "Units & Dimensions", "Weightage": "Low", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Kinematics", "Weightage": "Low", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Laws of Motion", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Work, Energy & Power", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Rotational Motion", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Gravitation", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Properties of Solids/Fluids", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Thermodynamics", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "KTG", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Oscillations & Waves", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Electrostatics", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Current Electricity", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Magnetism", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "EMI & AC", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "EM Waves", "Weightage": "Low", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Ray Optics", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Wave Optics", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Dual Nature", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Atoms & Nuclei", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Physics", "Chapter": "Semiconductors", "Weightage": "High", "Status": "Pending"},
    
    # CHEMISTRY
    {"Subject": "Chemistry", "Chapter": "Mole Concept", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Atomic Structure", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Chemical Bonding", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Thermodynamics", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Equilibrium", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Redox Reactions", "Weightage": "Low", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Solutions", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Electrochemistry", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Kinetics", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Surface Chemistry", "Weightage": "Low", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Periodic Table", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Metallurgy", "Weightage": "Low", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Block Elements (s, p, d, f)", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Coordination Compounds", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "GOC", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Hydrocarbons", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Haloalkanes/Haloarenes", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Alcohols, Phenols, Ethers", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Aldehydes & Ketones", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Amines", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Chemistry", "Chapter": "Biomolecules/Polymers", "Weightage": "Avg", "Status": "Pending"},

    # MATHS
    {"Subject": "Maths", "Chapter": "Sets, Relations, Functions", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Complex Numbers", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Quadratics", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Matrices & Determinants", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "P&C", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Binomial Theorem", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Sequence & Series", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Limits, Continuity, Diff", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Derivatives (AOD)", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Indefinite Integration", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Definite Integration", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Differential Equations", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Coordinate Geometry", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Vectors & 3D", "Weightage": "High", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Probability", "Weightage": "Avg", "Status": "Pending"},
    {"Subject": "Maths", "Chapter": "Statistics", "Weightage": "Low", "Status": "Pending"},
]

# --- 4. INITIALIZATION ---
if 'init' not in st.session_state:
    st.session_state['init'] = True
    st.session_state['syllabus'] = pd.DataFrame(FULL_SYLLABUS)
    st.session_state['target_exam'] = "JEE Main 2026"
    st.session_state['mock_avg'] = 120 # Default starting avg
    st.session_state['exam_config'] = {
        "JEE Main 2026": {"total": 300, "safe": 180, "date": date(2026, 1, 21)},
        "AP EAPCET 2026": {"total": 160, "safe": 120, "date": date(2026, 5, 19)}
    }

# --- 5. API SETUP ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_status = True
    else:
        api_status = False
except:
    api_status = False

# --- 6. CORE FUNCTIONS ---
def calculate_analytics(df, exam_mode):
    # Overall Completion
    total_ch = len(df)
    done_ch = len(df[df['Status'] != 'Pending'])
    completion_rate = (done_ch / total_ch) * 100
    
    # Subject Wise
    sub_data = {}
    for sub in ['Physics', 'Chemistry', 'Maths']:
        s_df = df[df['Subject'] == sub]
        s_done = len(s_df[s_df['Status'] != 'Pending'])
        sub_data[sub] = (s_done / len(s_df)) * 100 if len(s_df) > 0 else 0

    # Predictive Logic
    # Formula: (Mock% * 0.7) + (Syllabus% * 0.3)
    exam_total = st.session_state['exam_config'][exam_mode]['total']
    mock_perc = (st.session_state['mock_avg'] / exam_total) * 100
    
    readiness_score = (mock_perc * 0.7) + (completion_rate * 0.3)
    
    # Prediction Output
    if exam_mode.startswith("JEE"):
        # Rough Percentile Estimation based on readiness
        est_rank = int(1000000 * (1 - (readiness_score/100)))
        est_rank = max(1000, est_rank) # Cap at rank 1000 for realism
        pred_text = f"Est. Rank: {est_rank:,}"
    else:
        # EAPCET Rank
        est_rank = int(200000 * (1 - (readiness_score/100)))
        pred_text = f"Est. Rank: {est_rank:,}"
        
    return completion_rate, sub_data, pred_text, readiness_score

def ai_process_log(text):
    prompt = f"""
    You are the database engine for Project Zero Two.
    Task: specific chapter status update.
    User Text: "{text}"
    Master Chapters: {FULL_SYLLABUS[:5]} (and others).
    
    Return JSON list ONLY: [{{"Chapter": "Exact Name", "Status": "Mastered"}}]
    """
    try:
        response = model.generate_content(prompt)
        clean = response.text.replace("```json", "").replace("```", "").strip()
        updates = json.loads(clean)
        
        df = st.session_state['syllabus']
        count = 0
        for u in updates:
            # Fuzzy matching or direct (simplified here)
            mask = df['Chapter'].str.contains(u['Chapter'], case=False, regex=False)
            if mask.any():
                df.loc[mask, 'Status'] = u['Status']
                count += 1
        st.session_state['syllabus'] = df
        return f"SYNC COMPLETE: {count} CHAPTERS UPDATED."
    except:
        return "ERROR: AI COULD NOT PARSE COMMAND."

# --- 7. SIDEBAR ---
with st.sidebar:
    st.title("🔴 COMMANDER")
    
    # Goal Switcher
    st.markdown("### TARGET LOCK")
    target = st.selectbox("Select Mission", list(st.session_state['exam_config'].keys()))
    st.session_state['target_exam'] = target
    
    conf = st.session_state['exam_config'][target]
    days = (conf['date'] - date.today()).days
    
    st.metric("T-MINUS", f"{days} DAYS")
    st.progress(min(1.0, max(0.0, days/365)))
    
    st.markdown("---")
    uploaded_file = st.file_uploader("UPLOAD SCHEDULE (PDF)", type="pdf")
    st.markdown("---")
    st.caption("SYSTEM STATUS: " + ("ONLINE" if api_status else "OFFLINE"))

# --- 8. MAIN INTERFACE ---
st.title("PROJECT ZERO TWO")
st.caption(f"MISSION: {target.upper()} | ARCHITECT: SRIRAM")

tab1, tab2, tab3, tab4 = st.tabs(["📊 ANALYTICS CORE", "📝 SYLLABUS TRACKER", "🤖 COMMAND LOG", "💬 ZERO TWO"])

# --- TAB 1: ANALYTICS CORE ---
with tab1:
    # Calculate Data
    comp_rate, sub_data, pred_text, readiness = calculate_analytics(st.session_state['syllabus'], target)
    
    # Top Metrics (Glass Cards)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("PREDICTED OUTCOME", pred_text, delta="Based on trajectory")
    with c2:
        st.metric("SYLLABUS COMPLETED", f"{int(comp_rate)}%", delta=f"{len(st.session_state['syllabus'])} Chapters")
    with c3:
        st.metric("MOCK AVG", f"{st.session_state['mock_avg']}/{conf['total']}", delta="Last 3 tests")
    
    st.divider()
    
    # Graphs Row
    col_main, col_pie = st.columns([2, 1])
    
    with col_main:
        st.subheader("🚀 SUCCESS PROBABILITY")
        # Area Chart
        dates = [date.today() + timedelta(days=i) for i in range(10)]
        # Simulated projection
        proj_scores = [readiness + (i * 0.5) for i in range(10)] 
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=proj_scores, fill='tozeroy', mode='lines', line=dict(color='#ff003c', width=3), name='Trajectory'))
        fig.add_trace(go.Scatter(x=dates, y=[85]*10, mode='lines', line=dict(color='white', dash='dash'), name='Goal Line'))
        fig.update_layout(
            template="plotly_dark", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_pie:
        st.subheader("🎯 SUBJECT BREAKDOWN")
        # Create Donut Charts for Subjects
        for sub, val in sub_data.items():
            # Minimalist progress bars for subjects
            st.write(f"**{sub}**")
            st.progress(val/100)
            st.caption(f"{int(val)}% Mastered")

# --- TAB 2: SYLLABUS TRACKER ---
with tab2:
    st.subheader("🗂️ MASTER CODEX")
    st.info("Select a Subject to manage chapters. Changes auto-save.")
    
    sub_filter = st.selectbox("FILTER SUBJECT", ["Physics", "Chemistry", "Maths"])
    
    df = st.session_state['syllabus']
    filtered_df = df[df['Subject'] == sub_filter]
    
    # Interactive Editor
    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Mastery Status",
                options=["Pending", "Rev 1 Done", "Rev 2 Done", "Mastered"],
                required=True,
            ),
            "Weightage": st.column_config.TextColumn("Weightage", disabled=True),
        },
        num_rows="fixed"
    )
    
    # Save Logic
    if st.button("SAVE CHANGES"):
        # Update original DF with edits
        df.update(edited_df)
        st.session_state['syllabus'] = df
        st.success("DATABASE UPDATED")

# --- TAB 3: COMMAND LOG ---
with tab3:
    st.subheader("⌨️ MANUAL OVERRIDE")
    st.write("Type your progress naturally. The AI will update the Codex.")
    
    log_in = st.text_area("MISSION LOG", placeholder="Example: I mastered Rotational Motion and Electrostatics today.")
    
    if st.button("UPLOAD LOG"):
        if api_status:
            with st.spinner("ZERO TWO PROCESSING..."):
                msg = ai_process_log(log_in)
                st.success(msg)
        else:
            st.error("AI OFFLINE")

# --- TAB 4: ZERO TWO CHAT ---
with tab4:
    st.subheader("💬 TACTICAL ADVISOR")
    
    user_q = st.chat_input("Ask Zero Two...")
    if user_q:
        with st.chat_message("user"):
            st.write(user_q)
        
        if api_status:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    ctx = f"User Target: {target}. Syllabus %: {int(comp_rate)}%."
                    prompt = f"Act as Zero Two (Smart, Tactical, Professional). {ctx}. User: {user_q}"
                    res = model.generate_content(prompt)
                    st.write(res.text)
