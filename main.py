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

# --- 2. ZERO TWO THEME (BLACK & NEON RED) ---
st.markdown("""
<style>
    /* VOID BLACK BACKGROUND */
    .stApp { background-color: #050505; }
    
    /* NEON RED HEADERS */
    h1, h2, h3, h4 { 
        background: -webkit-linear-gradient(0deg, #ff003c, #ff80ab);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
    }
    
    /* METRICS */
    div[data-testid="stMetricValue"] {
        color: #ff003c; font-family: 'Courier New', monospace; text-shadow: 0 0 10px rgba(255, 0, 60, 0.4);
    }
    div[data-testid="stMetricLabel"] { color: #aaaaaa; }
    
    /* BUTTONS */
    .stButton>button {
        color: #ff003c; border: 1px solid #ff003c; background: #1a0b0e; border-radius: 0px;
    }
    .stButton>button:hover {
        background: #ff003c; color: white; box-shadow: 0 0 15px #ff003c;
    }
    
    /* PROGRESS BARS */
    .stProgress > div > div > div > div {
        background-color: #ff003c;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a0b0e; border: 1px solid #333; color: #fff;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        border-color: #ff003c; color: #ff003c;
    }
    
    /* EXPANDERS */
    .streamlit-expanderHeader {
        background-color: #111; color: #fff; border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. MASTER DATA (ACCURATE SYLLABUS) ---
def get_syllabus_data(exam_type):
    # BASE LIST (JEE MAIN - Based on your PDF Schedule)
    syllabus = [
        # PHYSICS
        {"Subject": "Physics", "Chapter": "Units, Dimensions & Errors", "Weightage": "Low"},
        {"Subject": "Physics", "Chapter": "Experimental Physics (Vernier/Screw Gauge)", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Kinematics (1D & Projectile)", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Laws of Motion & Friction", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Work, Energy & Power", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Centre of Mass & Collisions", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Rotational Motion", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Gravitation", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Solids & Fluids", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Thermal Properties", "Weightage": "Low"},
        {"Subject": "Physics", "Chapter": "Thermodynamics & KTG", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "SHM & Oscillations", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Waves & Sound", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Electrostatics", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Current Electricity", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Moving Charges & Magnetism", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "EMI & AC", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "EM Waves", "Weightage": "Low"},
        {"Subject": "Physics", "Chapter": "Ray Optics & Instruments", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Wave Optics", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Dual Nature of Radiation", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Atoms & Nuclei", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Semiconductors", "Weightage": "High"},
        # CHEMISTRY
        {"Subject": "Chemistry", "Chapter": "Mole Concept & Stoichiometry", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Redox & Titration", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Atomic Structure", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Periodic Table", "Weightage": "Low"},
        {"Subject": "Chemistry", "Chapter": "Chemical Bonding", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Thermodynamics", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Chemical Equilibrium", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Ionic Equilibrium", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Solutions", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Electrochemistry", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Chemical Kinetics", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "d and f Block Elements", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Coordination Compounds", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "GOC", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Hydrocarbons", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Haloalkanes & Haloarenes", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Alcohols, Phenols, Ethers", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Aldehydes, Ketones, Carboxylic", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Amines", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Biomolecules", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "POC (Purification & Detection)", "Weightage": "Avg"},
        # MATHS
        {"Subject": "Maths", "Chapter": "Sets, Relations & Functions", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Complex Numbers", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Quadratic Equations", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Matrices & Determinants", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Binomial Theorem", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Sequence & Series", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Limits, Continuity, Diff", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Application of Derivatives", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Indefinite Integration", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Definite Integration", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Areas", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Differential Equations", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Straight Lines", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Circles", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Parabola", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Ellipse & Hyperbola", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Vector Algebra", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "3D Geometry", "Weightage": "High"},
        {"Subject": "Maths", "Chapter": "Probability", "Weightage": "Avg"},
        {"Subject": "Maths", "Chapter": "Statistics", "Weightage": "Low"},
        {"Subject": "Maths", "Chapter": "Trigonometry", "Weightage": "Low"}
    ]

    # --- DYNAMIC ADDITIONS ---
    if exam_type == "AP EAPCET 2026":
        # Add DELETED CHAPTERS for EAPCET
        extras = [
            {"Subject": "Chemistry", "Chapter": "Solid State", "Weightage": "Avg"},
            {"Subject": "Chemistry", "Chapter": "Surface Chemistry", "Weightage": "Low"},
            {"Subject": "Chemistry", "Chapter": "Polymers", "Weightage": "Low"},
            {"Subject": "Chemistry", "Chapter": "Chemistry in Everyday Life", "Weightage": "Low"},
            {"Subject": "Chemistry", "Chapter": "Metallurgy", "Weightage": "Low"},
            {"Subject": "Maths", "Chapter": "Mathematical Induction", "Weightage": "Low"},
            {"Subject": "Physics", "Chapter": "Communication Systems", "Weightage": "Low"}
        ]
        syllabus.extend(extras)

    return syllabus

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
def calculate_metrics(df):
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
    return readiness, my_score, total_score

def get_subject_breakdown(df):
    data = {}
    for sub in ["Physics", "Chemistry", "Maths"]:
        sub_df = df[df['Subject'] == sub]
        if not sub_df.empty:
            w_score = sub_df['Weightage'].map({"High":3, "Avg":2, "Low":1}).sum()
            earned = 0
            for _, r in sub_df.iterrows():
                val = 0
                if r['Status'] == 'Mastered': val = 1
                elif r['Status'] == 'Revision 2': val = 0.8
                elif r['Status'] == 'Revision 1': val = 0.5
                earned += val * (3 if r['Weightage']=='High' else 2 if r['Weightage']=='Avg' else 1)
            data[sub] = int((earned/w_score)*100) if w_score > 0 else 0
    return data

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f: return json.load(f)
    return None

def save_profile(target, df_data, resources=None):
    if resources is None:
        # Preserve existing resources if not provided
        existing = load_profile()
        resources = existing.get('resources', []) if existing else []
        
    data = {
        "target": target, 
        "syllabus_data": df_data.to_dict('records'), 
        "resources": resources,
        "setup_complete": True
    }
    with open(PROFILE_FILE, 'w') as f: json.dump(data, f)
    return data

def ai_process_log(text, current_syllabus):
    valid_chaps = [x['Chapter'] for x in current_syllabus]
    prompt = f"Analyze: '{text}'. Valid Chapters: {valid_chaps}. Match user text to Valid Chapters. Return JSON: [{{'Chapter': 'Name', 'Status': 'Mastered'}}]"
    try:
        response = model.generate_content(prompt)
        clean = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except: return []

# --- 6. STARTUP WIZARD ---
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = load_profile()

if not st.session_state['user_profile']:
    st.title("🔴 SYSTEM INITIALIZATION")
    st.markdown("### TARGET PARAMETERS")
    
    target_sel = st.selectbox("MISSION GOAL", ["JEE Main 2026", "JEE Advanced 2026", "AP EAPCET 2026"])
    
    if 'wizard_df' not in st.session_state or st.session_state.get('last_wiz_target') != target_sel:
        raw_data = get_syllabus_data(target_sel)
        df_wiz = pd.DataFrame(raw_data)
        df_wiz['Status'] = 'Pending'
        df_wiz['Confidence'] = 0
        st.session_state['wizard_df'] = df_wiz
        st.session_state['last_wiz_target'] = target_sel
        st.rerun()

    st.info(f"Loading syllabus for {target_sel}...")
    
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
    resources = profile.get('resources', [])
    
    readiness, score, total_score = calculate_metrics(df)
    sub_breakdown = get_subject_breakdown(df)
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.image("logo.jpg", use_container_width=True)
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
        if energy < 40: st.error("⚠️ REST REQUIRED")

    # --- MAIN TABS ---
    st.title(f"PROJECT ZERO TWO: {target.upper()}")
    
    # Restoring ALL requested tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 DASHBOARD", "📝 CODEX", "⏱️ TIMER", "⚔️ ARMORY", "💬 ZERO TWO"])
    
    # TAB 1: DASHBOARD (Visuals & Logs)
    with tab1:
        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("READINESS SCORE", f"{readiness}%", "Weighted")
        c2.metric("SYLLABUS COUNT", f"{len(df)}", "Chapters")
        c3.metric("SYSTEM", "ONLINE", "Linked" if api_status else "Offline")
        
        st.divider()
        
        # PIE CHARTS (Restored)
        c_pie1, c_pie2, c_pie3 = st.columns(3)
        
        def make_donut(val, title, color):
            fig = go.Figure(data=[go.Pie(labels=['Done', 'Left'], values=[val, 100-val], hole=.7, marker_colors=[color, '#222'])])
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=120, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            return fig

        with c_pie1:
            st.caption("PHYSICS")
            st.plotly_chart(make_donut(sub_breakdown.get("Physics", 0), "Phy", "#00ccff"), use_container_width=True)
            st.markdown(f"**{sub_breakdown.get('Physics', 0)}%**")
            
        with c_pie2:
            st.caption("CHEMISTRY")
            st.plotly_chart(make_donut(sub_breakdown.get("Chemistry", 0), "Chem", "#ff003c"), use_container_width=True)
            st.markdown(f"**{sub_breakdown.get('Chemistry', 0)}%**")
            
        with c_pie3:
            st.caption("MATHS")
            st.plotly_chart(make_donut(sub_breakdown.get("Maths", 0), "Maths", "#ffcc00"), use_container_width=True)
            st.markdown(f"**{sub_breakdown.get('Maths', 0)}%**")

        st.divider()
        
        # TRAJECTORY GRAPH
        st.subheader("🚀 TRAJECTORY")
        dates = [date.today() + timedelta(days=i) for i in range(7)]
        # Dummy projection logic
        vals = [readiness + (i*0.5) for i in range(7)]
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=dates, y=vals, fill='tozeroy', mode='lines', line=dict(color='#ff003c')))
        fig_line.update_layout(template="plotly_dark", height=250, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.divider()
        
        # COMMAND LOG
        st.subheader("⌨️ COMMAND LOG")
        log_in = st.text_area("Mission Log", placeholder="Ex: I finished Electrostatics revision...")
        if st.button("UPLOAD LOG"):
            if api_status:
                ups = ai_process_log(log_in, profile['syllabus_data'])
                if ups:
                    for u in ups:
                        df.loc[df['Chapter'].str.contains(u['Chapter'], case=False), 'Status'] = u['Status']
                    save_profile(target, df, resources)
                    st.success("UPDATED")
                    st.rerun()

    # TAB 2: CODEX (Editor)
    with tab2:
        st.subheader(f"🗂️ SYLLABUS ({target})")
        sub = st.selectbox("Filter Subject", ["Physics", "Chemistry", "Maths"])
        fil_df = df[df['Subject'] == sub]
        
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
            save_profile(target, df, resources)
            st.success("SAVED")
            st.rerun()

    # TAB 3: TIMER (Restored)
    with tab3:
        st.subheader("⏱️ SYNC TIMER")
        t_min = st.number_input("Duration (Minutes)", 10, 180, 50)
        if st.button("INITIATE FOCUS LINK"):
            with st.status("ESTABLISHING LINK...", expanded=True):
                time.sleep(1)
                st.write("Blocking external signals...")
                time.sleep(1)
                st.write("Optimizing focus parameters...")
            st.success(f"TIMER ACTIVE: {t_min} MINS")

    # TAB 4: ARMORY (Restored)
    with tab4:
        st.subheader("⚔️ RESOURCE ARMORY")
        
        # Add new
        with st.expander("ADD RESOURCE"):
            r_name = st.text_input("Name")
            r_link = st.text_input("Link/Location")
            if st.button("STORE"):
                resources.append({"name": r_name, "link": r_link})
                save_profile(target, df, resources)
                st.rerun()
        
        # List
        if resources:
            for i, res in enumerate(resources):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{res['name']}**: [{res['link']}]({res['link']})")
                if c2.button("DEL", key=f"del_{i}"):
                    resources.pop(i)
                    save_profile(target, df, resources)
                    st.rerun()
        else:
            st.info("Armory Empty.")

    # TAB 5: CHAT
    with tab5:
        st.subheader("💬 ZERO TWO")
        q = st.chat_input("Ask...")
        if q and api_status:
            with st.chat_message("user"): st.write(q)
            with st.chat_message("assistant"):
                prompt = f"Act as Zero Two (Strategic AI). Exam: {target}. Readiness: {readiness}%. User: {q}"
                res = model.generate_content(prompt)
                st.write(res.text)
