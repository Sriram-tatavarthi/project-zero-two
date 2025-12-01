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
st.set_page_config(page_title="Project Zero Two", page_icon="🎓", layout="wide")

# --- 2. PROFESSIONAL EDTECH THEME (Light/Dark Compatible) ---
st.markdown("""
<style>
    /* Gradient Headers - Works in both modes */
    h1, h2, h3 { 
        background: -webkit-linear-gradient(0deg, #007CF0, #00DFD8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    
    /* Card Styling */
    div[data-testid="stMetricValue"] {
        font-size: 24px; color: #007CF0; font-weight: bold;
    }
    
    /* Tabs styling to look like Navigation Bar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 2px solid #f0f2f6;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 5px 5px 0px 0px;
        font-weight: 600;
        color: #555;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #007CF0;
        border-bottom: 3px solid #007CF0;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. MASTER DATA ---
def get_syllabus_data(exam_type):
    # ACCURATE SYLLABUS LIST
    syllabus = [
        # PHYSICS
        {"Subject": "Physics", "Chapter": "Units, Dimensions & Errors", "Weightage": "Low"},
        {"Subject": "Physics", "Chapter": "Experimental Physics", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Kinematics", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Laws of Motion", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Work, Energy & Power", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Rotational Motion", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Gravitation", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Solids & Fluids", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Thermodynamics & KTG", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "SHM & Waves", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Electrostatics", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Current Electricity", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Magnetism", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "EMI & AC", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Optics (Ray & Wave)", "Weightage": "High"},
        {"Subject": "Physics", "Chapter": "Modern Physics", "Weightage": "Avg"},
        {"Subject": "Physics", "Chapter": "Semiconductors", "Weightage": "High"},
        # CHEMISTRY
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
        {"Subject": "Chemistry", "Chapter": "GOC & Hydrocarbons", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Haloalkanes/Haloarenes", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Oxygen Compounds (Alc/Ald/Ket)", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Nitrogen Compounds", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Biomolecules", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "POC & Titration", "Weightage": "Avg"},
        # MATHS
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
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_status = True
    else:
        api_status = False
except:
    api_status = False

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
    total = df['W_Score'].sum()
    earned = df['Earned'].sum()
    return int((earned/total)*100) if total > 0 else 0

def get_subject_breakdown(df):
    data = {}
    for sub in ["Physics", "Chemistry", "Maths"]:
        sub_df = df[df['Subject'] == sub]
        if not sub_df.empty:
            w = sub_df['Weightage'].map({"High":3, "Avg":2, "Low":1}).sum()
            e = 0
            for _, r in sub_df.iterrows():
                val = 0
                if r['Status'] == 'Mastered': val = 1
                elif r['Status'] == 'Revision 2': val = 0.8
                elif r['Status'] == 'Revision 1': val = 0.5
                e += val * (3 if r['Weightage']=='High' else 2 if r['Weightage']=='Avg' else 1)
            data[sub] = int((e/w)*100) if w > 0 else 0
    return data

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f: return json.load(f)
    return None

def save_profile(target, df_data, resources=None, schedule_text=""):
    if resources is None:
        existing = load_profile()
        resources = existing.get('resources', []) if existing else []
    
    data = {
        "target": target, 
        "syllabus_data": df_data.to_dict('records'), 
        "resources": resources,
        "schedule_text": schedule_text,
        "setup_complete": True
    }
    with open(PROFILE_FILE, 'w') as f: json.dump(data, f)
    return data

def ai_process_log(text, current_syllabus):
    valid_chaps = [x['Chapter'] for x in current_syllabus]
    prompt = f"Analyze: '{text}'. Match to: {valid_chaps}. Return JSON: [{{'Chapter': 'Name', 'Status': 'Mastered'}}]"
    try:
        response = model.generate_content(prompt)
        clean = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except: return []

def parse_schedule_pdf(uploaded_file):
    reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages: text += page.extract_text()
    
    prompt = f"""
    Find exams/tests and key topics in this text. 
    Summarize what I need to do for the NEXT 7 DAYS.
    Keep it brief (bullet points).
    Text: {text[:3000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except: return "Could not parse schedule."

# --- 5. SETUP WIZARD ---
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = load_profile()

if not st.session_state['user_profile']:
    st.title("🚀 SYSTEM INITIALIZATION")
    st.markdown("### Welcome to Project Zero Two")
    target_sel = st.selectbox("Select Goal", ["JEE Main 2026", "JEE Advanced 2026", "AP EAPCET 2026"])
    
    if 'wizard_df' not in st.session_state or st.session_state.get('last_wiz_target') != target_sel:
        raw_data = get_syllabus_data(target_sel)
        df_wiz = pd.DataFrame(raw_data)
        df_wiz['Status'] = 'Pending'
        df_wiz['Confidence'] = 0
        st.session_state['wizard_df'] = df_wiz
        st.session_state['last_wiz_target'] = target_sel
        st.rerun()

    edited_df = st.data_editor(
        st.session_state['wizard_df'],
        use_container_width=True,
        column_config={
            "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Revision 1", "Revision 2", "Mastered"]),
            "Weightage": st.column_config.TextColumn("Impact", disabled=True),
            "Confidence": st.column_config.NumberColumn("Conf %", min_value=0, max_value=100)
        },
        height=400,
        hide_index=True
    )
    if st.button("Start Dashboard"):
        prof = save_profile(target_sel, edited_df)
        st.session_state['user_profile'] = prof
        st.rerun()

# --- 6. MAIN APPLICATION ---
else:
    profile = st.session_state['user_profile']
    target = profile['target']
    df = pd.DataFrame(profile['syllabus_data'])
    resources = profile.get('resources', [])
    schedule_text = profile.get('schedule_text', "No schedule uploaded.")
    
    readiness = calculate_metrics(df)
    sub_breakdown = get_subject_breakdown(df)

    # SIDEBAR
    with st.sidebar:
        st.title("PROJECT 02")
        st.caption(f"GOAL: {target}")
        
        if st.button("Reset / Change Goal"):
            os.remove(PROFILE_FILE)
            st.session_state['user_profile'] = None
            st.rerun()
        
        st.divider()
        uploaded_file = st.file_uploader("Upload Schedule (PDF)", type="pdf")
        if uploaded_file:
            if st.button("Analyze Schedule"):
                if api_status:
                    with st.spinner("Processing PDF..."):
                        schedule_text = parse_schedule_pdf(uploaded_file)
                        save_profile(target, df, resources, schedule_text)
                        st.success("Schedule Updated!")
                        st.rerun()

    # MAIN TABS (PROFESSIONAL NAMING)
    tab_home, tab_perf, tab_syll, tab_lib, tab_ai = st.tabs(["HOME", "PERFORMANCE", "SYLLABUS", "LIBRARY", "AI MENTOR"])

    # --- TAB 1: HOME (Daily Ops) ---
    with tab_home:
        # Top Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Readiness", f"{readiness}%", "Weighted Score")
        c2.metric("Chapters Done", f"{len(df[df['Status']=='Mastered'])}", f"of {len(df)}")
        c3.metric("AI Status", "Active" if api_status else "Offline")
        
        st.divider()
        
        col_schedule, col_log = st.columns([1, 1])
        
        with col_schedule:
            st.subheader("📅 Schedule & To-Do")
            st.info(schedule_text) # This shows the PDF summary
            
        with col_log:
            st.subheader("⌨️ Command Log")
            st.write("Update your progress naturally:")
            log_in = st.text_area("Log Input", placeholder="Ex: I finished Thermodynamics...")
            if st.button("Update Progress"):
                if api_status:
                    ups = ai_process_log(log_in, profile['syllabus_data'])
                    if ups:
                        for u in ups:
                            df.loc[df['Chapter'].str.contains(u['Chapter'], case=False), 'Status'] = u['Status']
                        save_profile(target, df, resources, schedule_text)
                        st.success("Updated!")
                        st.rerun()

    # --- TAB 2: PERFORMANCE (Analytics) ---
    with tab_perf:
        st.subheader("📊 Analytical Deep Dive")
        
        # Pie Charts
        c_p1, c_p2, c_p3 = st.columns(3)
        def make_donut(val, title, color):
            fig = go.Figure(data=[go.Pie(labels=['Done', 'Left'], values=[val, 100-val], hole=.7, marker_colors=[color, '#eee'])])
            fig.update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=140)
            return fig
            
        with c_p1:
            st.markdown("**Physics**")
            st.plotly_chart(make_donut(sub_breakdown.get("Physics",0), "Phy", "#007CF0"), use_container_width=True)
        with c_p2:
            st.markdown("**Chemistry**")
            st.plotly_chart(make_donut(sub_breakdown.get("Chemistry",0), "Chem", "#00DFD8"), use_container_width=True)
        with c_p3:
            st.markdown("**Maths**")
            st.plotly_chart(make_donut(sub_breakdown.get("Maths",0), "Math", "#7928CA"), use_container_width=True)

        st.divider()
        st.subheader("🚀 Projected Trajectory")
        dates = [date.today() + timedelta(days=i) for i in range(10)]
        vals = [readiness + (i*0.4) for i in range(10)]
        fig_line = go.Figure(go.Scatter(x=dates, y=vals, fill='tozeroy', line=dict(color='#007CF0')))
        fig_line.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_line, use_container_width=True)

    # --- TAB 3: SYLLABUS ---
    with tab_syll:
        st.subheader("🗂️ Codex")
        sub = st.selectbox("Subject Filter", ["Physics", "Chemistry", "Maths"])
        fil_df = df[df['Subject'] == sub]
        
        ed_df = st.data_editor(
            fil_df,
            use_container_width=True,
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Revision 1", "Revision 2", "Mastered"]),
                "Weightage": st.column_config.TextColumn("Impact", disabled=True),
                "Confidence": st.column_config.NumberColumn("Conf %", min_value=0, max_value=100)
            },
            hide_index=True
        )
        if st.button("Save Changes"):
            for i, r in ed_df.iterrows():
                mask = (df['Subject'] == r['Subject']) & (df['Chapter'] == r['Chapter'])
                df.loc[mask, 'Status'] = r['Status']
                df.loc[mask, 'Confidence'] = r['Confidence']
            save_profile(target, df, resources, schedule_text)
            st.success("Saved!")
            st.rerun()

    # --- TAB 4: LIBRARY ---
    with tab_lib:
        st.subheader("📚 Resource Library")
        with st.expander("Add New Link/Note"):
            r_name = st.text_input("Title")
            r_link = st.text_input("URL / Description")
            if st.button("Add to Library"):
                resources.append({"name": r_name, "link": r_link})
                save_profile(target, df, resources, schedule_text)
                st.rerun()
        
        if resources:
            for i, res in enumerate(resources):
                st.markdown(f"- **{res['name']}**: {res['link']}")
                if st.button(f"Delete '{res['name']}'", key=i):
                    resources.pop(i)
                    save_profile(target, df, resources, schedule_text)
                    st.rerun()
        else:
            st.info("Library is empty.")

    # --- TAB 5: AI MENTOR ---
    with tab_ai:
        st.subheader("💬 Tactical Advisor")
        q = st.chat_input("Ask for strategy...")
        if q and api_status:
            with st.chat_message("user"): st.write(q)
            with st.chat_message("assistant"):
                prompt = f"Act as an EdTech Academic Advisor. Goal: {target}. User Readiness: {readiness}%. Question: {q}"
                res = model.generate_content(prompt)
                st.write(res.text)
