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
    div[data-testid="stMetricValue"] {
        color: #ff003c; font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. MASTER DATA (FULL JEE MAIN SYLLABUS) ---
FULL_SYLLABUS = [
    # PHYSICS
    {"Subject": "Physics", "Chapter": "Units & Dimensions", "Confidence": 0}, 
    {"Subject": "Physics", "Chapter": "Kinematics", "Confidence": 0},
    {"Subject": "Physics", "Chapter": "Laws of Motion", "Confidence": 0}, 
    {"Subject": "Physics", "Chapter": "Work, Energy & Power", "Confidence": 0},
    {"Subject": "Physics", "Chapter": "Rotational Motion", "Confidence": 0}, 
    {"Subject": "Physics", "Chapter": "Gravitation", "Confidence": 0},
    {"Subject": "Physics", "Chapter": "Solids & Fluids", "Confidence": 0}, 
    {"Subject": "Physics", "Chapter": "Thermodynamics", "Confidence": 0},
    {"Subject": "Physics", "Chapter": "Kinetic Theory of Gases", "Confidence": 0}, 
    {"Subject": "Physics", "Chapter": "Oscillations & Waves", "Confidence": 0},
    {"Subject": "Physics", "Chapter": "Electrostatics", "Confidence": 0}, 
    {"Subject": "Physics", "Chapter": "Current Electricity", "Confidence": 0},
    {"Subject": "Physics", "Chapter": "Magnetism", "Confidence": 0}, 
    {"Subject": "Physics", "Chapter": "EMI & AC", "Confidence": 0},
    {"Subject": "Physics", "Chapter": "EM Waves", "Confidence": 0}, 
    {"Subject": "Physics", "Chapter": "Ray Optics", "Confidence": 0},
    {"Subject": "Physics", "Chapter": "Wave Optics", "Confidence": 0}, 
    {"Subject": "Physics", "Chapter": "Dual Nature of Matter", "Confidence": 0},
    {"Subject": "Physics", "Chapter": "Atoms & Nuclei", "Confidence": 0}, 
    {"Subject": "Physics", "Chapter": "Semiconductors", "Confidence": 0},
    
    # CHEMISTRY
    {"Subject": "Chemistry", "Chapter": "Mole Concept", "Confidence": 0}, 
    {"Subject": "Chemistry", "Chapter": "Atomic Structure", "Confidence": 0},
    {"Subject": "Chemistry", "Chapter": "Chemical Bonding", "Confidence": 0}, 
    {"Subject": "Chemistry", "Chapter": "Thermodynamics", "Confidence": 0},
    {"Subject": "Chemistry", "Chapter": "Equilibrium", "Confidence": 0}, 
    {"Subject": "Chemistry", "Chapter": "Redox Reactions", "Confidence": 0},
    {"Subject": "Chemistry", "Chapter": "Solutions", "Confidence": 0}, 
    {"Subject": "Chemistry", "Chapter": "Electrochemistry", "Confidence": 0},
    {"Subject": "Chemistry", "Chapter": "Chemical Kinetics", "Confidence": 0}, 
    {"Subject": "Chemistry", "Chapter": "Surface Chemistry", "Confidence": 0},
    {"Subject": "Chemistry", "Chapter": "Periodicity", "Confidence": 0}, 
    {"Subject": "Chemistry", "Chapter": "p-Block Elements", "Confidence": 0},
    {"Subject": "Chemistry", "Chapter": "d and f Block Elements", "Confidence": 0}, 
    {"Subject": "Chemistry", "Chapter": "Coordination Compounds", "Confidence": 0},
    {"Subject": "Chemistry", "Chapter": "GOC", "Confidence": 0}, 
    {"Subject": "Chemistry", "Chapter": "Hydrocarbons", "Confidence": 0},
    {"Subject": "Chemistry", "Chapter": "Haloalkanes & Haloarenes", "Confidence": 0}, 
    {"Subject": "Chemistry", "Chapter": "Alcohols, Phenols, Ethers", "Confidence": 0},
    {"Subject": "Chemistry", "Chapter": "Aldehydes, Ketones, Carboxylic", "Confidence": 0}, 
    {"Subject": "Chemistry", "Chapter": "Amines", "Confidence": 0},
    {"Subject": "Chemistry", "Chapter": "Biomolecules", "Confidence": 0},

    # MATHS
    {"Subject": "Maths", "Chapter": "Sets, Relations & Functions", "Confidence": 0}, 
    {"Subject": "Maths", "Chapter": "Complex Numbers", "Confidence": 0},
    {"Subject": "Maths", "Chapter": "Quadratic Equations", "Confidence": 0}, 
    {"Subject": "Maths", "Chapter": "Matrices & Determinants", "Confidence": 0},
    {"Subject": "Maths", "Chapter": "Permutations & Combinations", "Confidence": 0}, 
    {"Subject": "Maths", "Chapter": "Binomial Theorem", "Confidence": 0},
    {"Subject": "Maths", "Chapter": "Sequence & Series", "Confidence": 0}, 
    {"Subject": "Maths", "Chapter": "Limits, Continuity, Diff", "Confidence": 0},
    {"Subject": "Maths", "Chapter": "Application of Derivatives", "Confidence": 0}, 
    {"Subject": "Maths", "Chapter": "Indefinite Integration", "Confidence": 0},
    {"Subject": "Maths", "Chapter": "Definite Integration", "Confidence": 0}, 
    {"Subject": "Maths", "Chapter": "Differential Equations", "Confidence": 0},
    {"Subject": "Maths", "Chapter": "Straight Lines & Circles", "Confidence": 0}, 
    {"Subject": "Maths", "Chapter": "Conic Sections", "Confidence": 0},
    {"Subject": "Maths", "Chapter": "Vector Algebra", "Confidence": 0}, 
    {"Subject": "Maths", "Chapter": "3D Geometry", "Confidence": 0},
    {"Subject": "Maths", "Chapter": "Probability", "Confidence": 0}, 
    {"Subject": "Maths", "Chapter": "Statistics", "Confidence": 0},
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
def save_profile_from_editor(target, edited_df):
    profile_data = {
        "target": target,
        "syllabus_data": edited_df.to_dict('records'),
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

def update_profile_file(df_data, target_exam):
    profile_data = {
        "target": target_exam,
        "syllabus_data": df_data.to_dict('records'),
        "setup_complete": True
    }
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profile_data, f)

def ai_process_log(text):
    prompt = f"Analyze: '{text}'. Identify chapters from JEE syllabus. Return JSON: [{{'Chapter': 'Name', 'Status': 'Mastered'}}]"
    try:
        response = model.generate_content(prompt)
        clean = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return []

# --- 6. SETUP WIZARD (Now with Full Editor) ---
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = load_profile()

if not st.session_state['user_profile']:
    st.title("🔴 SYSTEM INITIALIZATION")
    st.markdown("Welcome, Pilot. Let's calibrate your system parameters.")
    
    with st.container():
        st.markdown("### STEP 1: TARGET LOCK")
        target_sel = st.selectbox("Select Mission Goal", ["JEE Main 2026", "AP EAPCET 2026", "BITSAT 2026"])
        
        st.divider()
        st.markdown("### STEP 2: SYLLABUS AUDIT")
        st.info("Mark your current progress. You can edit this later in the Dashboard.")
        
        # Prepare Initial Dataframe
        if 'wizard_df' not in st.session_state:
            init_df = pd.DataFrame(FULL_SYLLABUS)
            init_df['Status'] = 'Pending'
            st.session_state['wizard_df'] = init_df
        
        # FULL EDITOR IN WIZARD
        edited_wizard_df = st.data_editor(
            st.session_state['wizard_df'],
            use_container_width=True,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Pending", "Revision 1", "Revision 2", "Mastered"],
                    required=True
                ),
                "Confidence": st.column_config.NumberColumn(
                    "Confidence (%)",
                    min_value=0, 
                    max_value=100,
                    step=5,
                    format="%d%%"
                ),
                "Chapter": st.column_config.TextColumn("Chapter", disabled=True),
                "Subject": st.column_config.TextColumn("Subject", disabled=True)
            },
            hide_index=True,
            height=500 
        )
        
        st.divider()
        
        if st.button("INITIALIZE SYSTEM"):
            with st.spinner("SAVING CONFIGURATION..."):
                time.sleep(1)
                profile = save_profile_from_editor(target_sel, edited_wizard_df)
                st.session_state['user_profile'] = profile
                st.rerun()

# --- 7. MAIN DASHBOARD ---
else:
    # Load Data
    profile = st.session_state['user_profile']
    df = pd.DataFrame(profile['syllabus_data'])
    target_exam = profile['target']
    
    # Sidebar
    with st.sidebar:
        st.title("🔴 COMMANDER")
        st.caption(f"TARGET: {target_exam}")
        if st.button("RESET SYSTEM (CLEAR DATA)"):
            if os.path.exists(PROFILE_FILE):
                os.remove(PROFILE_FILE)
            st.session_state['user_profile'] = None
            st.rerun()
        st.divider()
        uploaded_file = st.file_uploader("SCHEDULE UPLINK (PDF)", type="pdf")

    # Metrics
    total = len(df)
    mastered = len(df[df['Status'] == 'Mastered'])
    revised = len(df[df['Status'].str.contains('Revision', na=False)])
    perc = int(((mastered + (revised * 0.5))/total)*100)

    # UI
    st.title("PROJECT ZERO TWO")
    
    tab1, tab2, tab3 = st.tabs(["📊 DASHBOARD", "📝 SYLLABUS TRACKER", "🤖 ZERO TWO"])
    
    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("PREDICTED RANK", "4,200", "Est")
        c2.metric("SYLLABUS SYNC", f"{perc}%", f"{mastered} Mastered / {revised} Revised")
        c3.metric("SYSTEM STATUS", "ONLINE", "Ai Linked" if api_status else "Offline")
        
        st.divider()
        st.subheader("⌨️ COMMAND LOG")
        log_txt = st.text_area("Enter Daily Progress", placeholder="I finished Electrostatics today...")
        if st.button("UPLOAD LOG"):
            if api_status:
                updates = ai_process_log(log_txt)
                if updates:
                    for u in updates:
                        df.loc[df['Chapter'].str.contains(u['Chapter'], case=False), 'Status'] = u['Status']
                    update_profile_file(df, target_exam)
                    st.success(f"UPDATED {len(updates)} MODULES")
                    st.rerun()
            else:
                st.error("AI OFFLINE")

    with tab2:
        st.subheader("🗂️ MASTER CODEX")
        st.info("Edit the Status and Confidence directly in the table below.")
        
        sub_view = st.selectbox("FILTER SUBJECT", ["Physics", "Chemistry", "Maths"])
        
        filtered_df = df[df['Subject'] == sub_view]
        
        # THE EDITABLE TABLE (Dashboard Version)
        edited_df = st.data_editor(
            filtered_df,
            use_container_width=True,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Pending", "Revision 1", "Revision 2", "Mastered"],
                    required=True
                ),
                "Confidence": st.column_config.NumberColumn(
                    "Confidence (%)",
                    min_value=0,
                    max_value=100,
                    step=5,
                    format="%d%%"
                ),
                "Chapter": st.column_config.TextColumn("Chapter", disabled=True),
                "Subject": st.column_config.TextColumn("Subject", disabled=True)
            },
            hide_index=True
        )
        
        if st.button("SAVE CHANGES TO DATABASE"):
            for index, row in edited_df.iterrows():
                mask = (df['Subject'] == row['Subject']) & (df['Chapter'] == row['Chapter'])
                df.loc[mask, 'Status'] = row['Status']
                df.loc[mask, 'Confidence'] = row['Confidence']
            
            update_profile_file(df, target_exam)
            st.success("DATABASE SYNCHRONIZED")
            st.rerun()
        
    with tab3:
        st.subheader("💬 TACTICAL ADVISOR")
        q = st.chat_input("Ask Zero Two...")
        if q and api_status:
            with st.chat_message("user"): st.write(q)
            with st.chat_message("assistant"):
                res = model.generate_content(f"Act as Zero Two. User: {q}")
                st.write(res.text)
