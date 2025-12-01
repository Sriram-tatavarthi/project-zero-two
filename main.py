import streamlit as st
import pandas as pd
import datetime
from datetime import date, timedelta
import google.generativeai as genai
import plotly.graph_objects as go
import time
import pypdf
import json
import os

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Project Zero Two", page_icon="🔴", layout="wide")

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
    .stButton>button {
        color: #ff003c; border: 1px solid #ff003c; background: #1a0b0e;
    }
    .stButton>button:hover {
        background: #ff003c; color: white;
    }
    /* Wizard Container */
    .wizard-box {
        border: 1px solid #333; padding: 30px; border-radius: 15px;
        background: rgba(20,20,20,0.8); text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. MASTER DATA (The Syllabus) ---
FULL_SYLLABUS = [
    {"Subject": "Physics", "Chapter": "Units & Dimensions"}, {"Subject": "Physics", "Chapter": "Kinematics"},
    {"Subject": "Physics", "Chapter": "Laws of Motion"}, {"Subject": "Physics", "Chapter": "Work Energy Power"},
    {"Subject": "Physics", "Chapter": "Rotational Motion"}, {"Subject": "Physics", "Chapter": "Gravitation"},
    {"Subject": "Physics", "Chapter": "Thermodynamics"}, {"Subject": "Physics", "Chapter": "Electrostatics"},
    {"Subject": "Physics", "Chapter": "Current Electricity"}, {"Subject": "Physics", "Chapter": "Magnetism"},
    {"Subject": "Physics", "Chapter": "Ray Optics"}, {"Subject": "Physics", "Chapter": "Wave Optics"},
    {"Subject": "Physics", "Chapter": "Semiconductors"}, {"Subject": "Physics", "Chapter": "Modern Physics"},
    {"Subject": "Chemistry", "Chapter": "Mole Concept"}, {"Subject": "Chemistry", "Chapter": "Atomic Structure"},
    {"Subject": "Chemistry", "Chapter": "Chemical Bonding"}, {"Subject": "Chemistry", "Chapter": "Thermodynamics"},
    {"Subject": "Chemistry", "Chapter": "Equilibrium"}, {"Subject": "Chemistry", "Chapter": "Electrochemistry"},
    {"Subject": "Chemistry", "Chapter": "Chemical Kinetics"}, {"Subject": "Chemistry", "Chapter": "Coordination Comp"},
    {"Subject": "Chemistry", "Chapter": "GOC"}, {"Subject": "Chemistry", "Chapter": "Hydrocarbons"},
    {"Subject": "Chemistry", "Chapter": "Aldehydes & Ketones"}, {"Subject": "Maths", "Chapter": "Sets & Functions"},
    {"Subject": "Maths", "Chapter": "Complex Numbers"}, {"Subject": "Maths", "Chapter": "Quadratic Eq"},
    {"Subject": "Maths", "Chapter": "Matrices & Det"}, {"Subject": "Maths", "Chapter": "Permutation & Comb"},
    {"Subject": "Maths", "Chapter": "Binomial Thm"}, {"Subject": "Maths", "Chapter": "Sequence & Series"},
    {"Subject": "Maths", "Chapter": "Limits & Continuity"}, {"Subject": "Maths", "Chapter": "Derivatives"},
    {"Subject": "Maths", "Chapter": "Integration (Indef)"}, {"Subject": "Maths", "Chapter": "Integration (Def)"},
    {"Subject": "Maths", "Chapter": "Differential Eq"}, {"Subject": "Maths", "Chapter": "Vectors"},
    {"Subject": "Maths", "Chapter": "3D Geometry"}, {"Subject": "Maths", "Chapter": "Probability"}
]
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

# --- 5. FUNCTIONS ---
def save_profile(target, completed_chapters):
    # Create the dataframe structure
    df = pd.DataFrame(FULL_SYLLABUS)
    df['Status'] = 'Pending'
    # Mark completed
    df.loc[df['Chapter'].isin(completed_chapters), 'Status'] = 'Mastered'
    
    profile_data = {
        "target": target,
        "syllabus_data": df.to_dict('records'),
        "setup_complete": True
    }
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profile_data, f)
    return profile_data

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            return json.load(f)
    return None

def ai_process_log(text):
    prompt = f"Analyze: '{text}'. Identify chapters from JEE syllabus. Return JSON: [{{'Chapter': 'Name', 'Status': 'Mastered'}}]"
    try:
        response = model.generate_content(prompt)
        clean = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return []

# --- 6. SETUP WIZARD LOGIC ---
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = load_profile()

# If profile doesn't exist, SHOW WIZARD
if not st.session_state['user_profile']:
    st.title("🔴 SYSTEM INITIALIZATION")
    st.markdown("Welcome, Pilot. Let's calibrate your system parameters.")
    
    with st.container():
        st.markdown("### STEP 1: TARGET LOCK")
        target_sel = st.selectbox("Select Mission Goal", ["JEE Main 2026", "AP EAPCET 2026", "BITSAT 2026"])
        
        st.divider()
        
        st.markdown("### STEP 2: SYLLABUS AUDIT")
        st.info("Select chapters you have ALREADY completed/revised.")
        
        # Get list of all chapters
        all_chaps = [x['Chapter'] for x in FULL_SYLLABUS]
        completed = st.multiselect("Completed Modules", all_chaps)
        
        st.divider()
        
        if st.button("INITIALIZE SYSTEM"):
            with st.spinner("SAVING CONFIGURATION..."):
                time.sleep(1)
                profile = save_profile(target_sel, completed)
                st.session_state['user_profile'] = profile
                st.rerun()

# --- 7. MAIN DASHBOARD (WAR MODE) ---
else:
    # Load Data
    profile = st.session_state['user_profile']
    df = pd.DataFrame(profile['syllabus_data'])
    target_exam = profile['target']
    
    # Sidebar
    with st.sidebar:
        st.title("🔴 COMMANDER")
        st.caption(f"TARGET: {target_exam}")
        if st.button("RESET SYSTEM"):
            if os.path.exists(PROFILE_FILE):
                os.remove(PROFILE_FILE)
            st.session_state['user_profile'] = None
            st.rerun()
            
        st.divider()
        uploaded_file = st.file_uploader("SCHEDULE UPLINK (PDF)", type="pdf")

    # Metrics Calculation
    total = len(df)
    done = len(df[df['Status'] == 'Mastered'])
    perc = int((done/total)*100)

    # UI
    st.title("PROJECT ZERO TWO")
    
    tab1, tab2, tab3 = st.tabs(["📊 DASHBOARD", "📝 SYLLABUS", "🤖 ZERO TWO"])
    
    with tab1:
        # Glass Cards
        c1, c2, c3 = st.columns(3)
        c1.metric("PREDICTED RANK", "4,200", "Est")
        c2.metric("SYLLABUS SYNC", f"{perc}%", f"{done}/{total} Chaps")
        c3.metric("SYSTEM STATUS", "ONLINE", "Ai Linked" if api_status else "Offline")
        
        st.divider()
        
        # Log Entry
        st.subheader("⌨️ COMMAND LOG")
        log_txt = st.text_area("Enter Daily Progress", placeholder="I finished Electrostatics today...")
        if st.button("UPLOAD LOG"):
            if api_status:
                updates = ai_process_log(log_txt)
                if updates:
                    for u in updates:
                        df.loc[df['Chapter'].str.contains(u['Chapter'], case=False), 'Status'] = u['Status']
                    
                    # Save back to file
                    profile['syllabus_data'] = df.to_dict('records')
                    with open(PROFILE_FILE, 'w') as f:
                        json.dump(profile, f)
                    st.success(f"UPDATED {len(updates)} MODULES")
                    st.rerun()
            else:
                st.error("AI OFFLINE")

    with tab2:
        st.subheader("🗂️ MASTER CODEX")
        sub_view = st.selectbox("Filter", ["Physics", "Chemistry", "Maths"])
        st.dataframe(
            df[df['Subject'] == sub_view], 
            use_container_width=True,
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Mastered"])
            }
        )
        
    with tab3:
        st.subheader("💬 TACTICAL ADVISOR")
        q = st.chat_input("Ask Zero Two...")
        if q and api_status:
            with st.chat_message("user"): st.write(q)
            with st.chat_message("assistant"):
                res = model.generate_content(f"Act as Zero Two. User: {q}")
                st.write(res.text)
