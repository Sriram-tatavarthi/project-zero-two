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
st.set_page_config(page_title="Project Zero Two: MK X", page_icon="🔴", layout="wide")

# --- 2. THEME & CSS ---
st.markdown("""
<style>
    .stApp { background-color: #050505; }
    h1, h2, h3 { 
        background: -webkit-linear-gradient(0deg, #ff003c, #ff80ab);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Courier New', monospace;
    }
    div[data-testid="stMetricValue"] {
        color: #ff003c; font-family: 'Courier New', monospace; text-shadow: 0 0 10px rgba(255, 0, 60, 0.3);
    }
    .stButton>button {
        color: #ff003c; border: 1px solid #ff003c; background: #1a0b0e;
    }
    .stButton>button:hover {
        background: #ff003c; color: white;
    }
    .high-weight { color: #ff003c; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. DYNAMIC SYLLABUS DATABASE ---
def get_syllabus_data(exam_type):
    """Returns the specific chapter list and weightage for the selected exam."""
    
    # CORE LIST (Common to JEE Main/Advanced)
    core_physics = [
        {"Subject": "Physics", "Chapter": "Modern Physics", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Current Electricity", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Electrostatics", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Ray Optics", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Thermodynamics & KTG", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Rotational Motion", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Kinematics", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Gravitation", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Work, Energy, Power", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Laws of Motion", "Weightage": "Low"},
        {"Subject": "Physics", "Chapter": "Semiconductors", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "AC & EMI", "Weightage": "Avg"}
    ]
    
    core_chem = [
        {"Subject": "Chemistry", "Chapter": "Coordination Compounds", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "GOC", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Thermodynamics", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Chemical Bonding", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Electrochemistry", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Atomic Structure", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Solutions", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Equilibrium", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Kinetics", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Mole Concept", "Weightage": "Low"}
    ]
    
    core_maths = [
        {"Subject": "Maths", "Chapter": "Vectors & 3D", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Definite Integration", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Matrices & Determinants", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Sequence & Series", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Probability", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Circle & Conics", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Complex Numbers", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Functions", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Limits & Derivatives", "Weightage": "Avg"}
    ]
    
    base_syllabus = core_physics + core_chem + core_maths

    # --- EXAM SPECIFIC ADJUSTMENTS ---
    if exam_type == "AP EAPCET 2026":
        extras = [
            {"Subject": "Chemistry", "Chapter": "Solid State", "Weightage": "Avg"},
            {"Subject": "Chemistry", "Chapter": "Surface Chemistry", "Weightage": "Low"},
            {"Subject": "Chemistry", "Chapter": "Polymers", "Weightage": "Low"},
            {"Subject": "Chemistry", "Chapter": "Chemistry in Everyday Life", "Weightage": "Low"},
            {"Subject": "Chemistry", "Chapter": "s-Block Elements", "Weightage": "Low"},
            {"Subject": "Chemistry", "Chapter": "Metallurgy", "Weightage": "Low"},
            {"Subject": "Maths", "Chapter": "Mathematical Induction", "Weightage": "Low"},
            {"Subject": "Physics", "Chapter": "Communication Systems", "Weightage": "Low"}
        ]
        return base_syllabus + extras

    elif exam_type == "JEE Advanced 2026":
        for item in base_syllabus:
            if item['Chapter'] == "Rotational Motion": item['Weightage'] = "High" 
            if item['Chapter'] == "Semiconductors": item['Weightage'] = "Low" 
            if item['Chapter'] == "Complex Numbers": item['Weightage'] = "High"
        return base_syllabus

    else: # JEE Main 2026
        return base_syllabus

PROFILE_FILE = "user_profile.json"

# --- 4. API SETUP ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_status = True
    else:
        api_status = False
except:
    api_status = False

# --- 5. LOGIC & SCORING ---
def calculate_metrics(df, exam):
    w_vals = {"High": 3, "Avg": 2, "Low": 1}
    df['W_Score'] = df['Weightage'].map(w_vals)
    df['Earned'] = 0.0
    
    for i, row in df.iterrows():
        val = 0.0
        if row['Status'] == 'Mastered': val = 1.0
        elif row['Status'] == 'Revision 2': val = 0.8
        elif row['Status'] == 'Revision 1': val = 0.5
        df.at[i, 'Earned'] = val * row['W_Score']
        
    total_score = df['W_Score'].sum()
    my_score = df['Earned'].sum()
    readiness = int((my_score / total_score) * 100) if total_score > 0 else 0
    return readiness

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f: return json.load(f)
    return None

def save_profile(target, df_data):
    data = {
        "target": target, 
        "syllabus_data": df_data.to_dict('records'), 
        "setup_complete": True
    }
    with open(PROFILE_FILE, 'w') as f: json.dump(data, f)
    return data

def ai_process_log(text, current_syllabus):
    valid_chaps = [x['Chapter'] for x in current_syllabus]
    prompt = f"""
    Analyze: '{text}'. 
    Valid Chapters for this exam: {valid_chaps}
    Task: Match user text to Valid Chapters.
    Return JSON: [{{'Chapter': 'Exact Name From List', 'Status': 'Mastered'}}]
    """
    try:
        response = model.generate_content(prompt)
        clean = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except: return []

# --- 6. STARTUP WIZARD ---
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = load_profile()

if not st.session_state['user_profile']:
    st.title("🔴 MK X INITIALIZATION")
    st.markdown("### DYNAMIC CALIBRATION")
    
    target_sel = st.selectbox(
        "MISSION GOAL", 
        ["JEE Main 2026", "JEE Advanced 2026", "AP EAPCET 2026"],
        index=0
    )
    
    # Load specific chapters
    if 'current_exam_wiz' not in st.session_state or st.session_state['current_exam_wiz'] != target_sel:
        raw_data = get_syllabus_data(target_sel)
        df_wiz = pd.DataFrame(raw_data)
        df_wiz['Status'] = 'Pending'
        df_wiz['Confidence'] = 0
        st.session_state['wizard_df'] = df_wiz
        st.session_state['current_exam_wiz'] = target_sel
        st.rerun() 

    st.info(f"Loaded {len(st.session_state['wizard_df'])} chapters for {target_sel}.")
    
    # --- FIXED COLUMN NAME HERE ---
    edited_df = st.data_editor(
        st.session_state['wizard_df'],
        use_container_width=True,
        column_config={
            "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Revision 1", "Revision 2", "Mastered"]),
            "Weightage": st.column_config.TextColumn("Impact", disabled=True),
            "Confidence": st.column_config.NumberColumn("Confidence (%)", min_value=0, max_value=100)
        },
        height=400,
        hide_index=True
    )
    
    if st.button("ENGAGE SYSTEM"):
        with st.spinner("SAVING CONFIGURATION..."):
            time.sleep(1)
            prof = save_profile(target_sel, edited_df)
            st.session_state['user_profile'] = prof
            st.rerun()

# --- 7. MAIN DASHBOARD ---
else:
    profile = st.session_state['user_profile']
    target = profile['target']
    df = pd.DataFrame(profile['syllabus_data'])
    
    readiness = calculate_metrics(df, target)
    
    # SIDEBAR
    with st.sidebar:
        st.title("🔴 COMMANDER")
        st.caption(f"TARGET: {target}")
        
        if st.button("CHANGE MISSION (RESET)"):
            os.remove(PROFILE_FILE)
            st.session_state['user_profile'] = None
            st.rerun()
            
        st.divider()
        uploaded_file = st.file_uploader("SCHEDULE PDF", type="pdf")
        
        st.divider()
        st.markdown("### VITALITY")
        energy = st.slider("Energy", 0, 100, 80)
        if energy < 40: st.error("REST REQUIRED")

    # MAIN UI
    st.title(f"PROJECT ZERO TWO: {target.upper()}")
    
    tab1, tab2, tab3 = st.tabs(["📊 STRATEGY", "📝 CODEX", "🤖 ADVISOR"])
    
    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("READINESS SCORE", f"{readiness}%", "Weighted")
        c2.metric("CHAPTERS TRACKED", f"{len(df)}", "Exam Specific")
        c3.metric("SYSTEM", "ONLINE", "Linked" if api_status else "Offline")
        
        st.progress(readiness/100)
        
        high_risk = df[(df['Weightage'] == 'High') & (df['Status'] == 'Pending')]
        if not high_risk.empty:
            st.error(f"⚠️ You have {len(high_risk)} HIGH IMPACT chapters pending!")
        
        st.divider()
        st.subheader("⌨️ COMMAND LOG")
        log_in = st.text_area("Update Status")
        if st.button("UPLOAD"):
            if api_status:
                ups = ai_process_log(log_in, profile['syllabus_data'])
                if ups:
                    for u in ups:
                        df.loc[df['Chapter'].str.contains(u['Chapter'], case=False), 'Status'] = u['Status']
                    save_profile(target, df)
                    st.success("UPDATED")
                    st.rerun()

    with tab2:
        st.subheader(f"🗂️ SYLLABUS ({target})")
        sub = st.selectbox("Filter Subject", ["Physics", "Chemistry", "Maths"])
        
        fil_df = df[df['Subject'] == sub]
        
        # --- FIXED COLUMN NAME HERE TOO ---
        ed_df = st.data_editor(
            fil_df,
            use_container_width=True,
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Revision 1", "Revision 2", "Mastered"]),
                "Weightage": st.column_config.TextColumn("Impact", disabled=True),
                "Confidence": st.column_config.NumberColumn("Confidence (%)", min_value=0, max_value=100)
            },
            hide_index=True
        )
        if st.button("SAVE CODEX CHANGES"):
            for i, r in ed_df.iterrows():
                mask = (df['Subject'] == r['Subject']) & (df['Chapter'] == r['Chapter'])
                df.loc[mask, 'Status'] = r['Status']
                df.loc[mask, 'Confidence'] = r['Confidence']
            save_profile(target, df)
            st.success("SAVED")
            st.rerun()

    with tab3:
        st.subheader("💬 ZERO TWO")
        q = st.chat_input("Ask...")
        if q and api_status:
            with st.chat_message("user"): st.write(q)
            with st.chat_message("assistant"):
                prompt = f"Act as Zero Two (Strategic AI). Exam: {target}. Readiness: {readiness}%. User: {q}"
                res = model.generate_content(prompt)
                st.write(res.text)
