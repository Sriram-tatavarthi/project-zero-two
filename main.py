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

# --- 2. DYNAMIC THEME ENGINE (FIXED VISIBILITY) ---
def apply_theme(theme_name):
    if theme_name == "Zero Two (Dark)":
        # VOID BLACK & NEON RED
        st.markdown("""
        <style>
            .stApp { background-color: #050505; color: #e0e0e0; }
            h1, h2, h3, h4 { 
                background: -webkit-linear-gradient(0deg, #ff003c, #ff80ab);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-family: 'Helvetica Neue', sans-serif; font-weight: 800;
            }
            div[data-testid="stMetricValue"] { color: #ff003c; }
            .stProgress > div > div > div > div { background-color: #ff003c; }
            .stButton>button {
                color: #ff003c; border: 1px solid #ff003c; background: #1a0b0e;
            }
            div[data-testid="stContainer"] {
                border: 1px solid #333; background-color: #0a0a0a; border-radius: 10px; padding: 15px;
            }
            /* Make text readable in expanders */
            .streamlit-expanderContent { color: #e0e0e0; }
        </style>
        """, unsafe_allow_html=True)
    else:
        # EDTECH (Light) - FIXED CONTRAST
        st.markdown("""
        <style>
            .stApp { background-color: #f4f7f6; color: #2d3436; }
            h1, h2, h3, h4 { 
                background: -webkit-linear-gradient(0deg, #0984e3, #00cec9);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-family: 'Verdana', sans-serif; font-weight: 700;
            }
            div[data-testid="stMetricValue"] { color: #0984e3; }
            .stProgress > div > div > div > div { background-image: linear-gradient(90deg, #0984e3, #00cec9); }
            .stButton>button {
                color: white; border: none; background: linear-gradient(90deg, #0984e3, #00cec9);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            div[data-testid="stContainer"] {
                background-color: #ffffff; border-radius: 15px; padding: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;
            }
            /* Fix Text Visibility */
            p, li, span, div { color: #2d3436; }
            .streamlit-expanderHeader { color: #2d3436; font-weight: 600; }
        </style>
        """, unsafe_allow_html=True)

# --- 3. MASTER DATA ---
def get_syllabus_data(exam_type):
    syllabus = [
        # PHYSICS
        {"Subject": "Physics", "Chapter": "Units & Errors", "Weightage": "Low"},
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
        {"Subject": "Chemistry", "Chapter": "GOC", "Weightage": "High"},
        {"Subject": "Chemistry", "Chapter": "Hydrocarbons", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Haloalkanes/Haloarenes", "Weightage": "Avg"},
        {"Subject": "Chemistry", "Chapter": "Oxygen Compounds", "Weightage": "High"},
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
model = None
api_status = False
status_msg = "Initializing..."

def init_ai():
    if "GEMINI_API_KEY" not in st.secrets:
        return None, False, "Error: Key Missing"
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    candidates = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
    for m in candidates:
        try:
            test_model = genai.GenerativeModel(m)
            test_model.generate_content("test")
            return test_model, True, "Active"
        except:
            continue
    return None, False, "Connection Failed"

model, api_status, status_msg = init_ai()

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
        
    total_points = df['W_Score'].sum()
    earned_points = df['Impact_Score'].sum()
    readiness = int((earned_points / total_points) * 100) if total_points > 0 else 0
    
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

def save_profile(target, df_data, resources=None, schedule_text="", test_scores=None):
    if resources is None:
        existing = load_profile()
        resources = existing.get('resources', []) if existing else []
    if test_scores is None:
        existing = load_profile()
        test_scores = existing.get('test_scores', []) if existing else []
    
    data = {
        "target": target, 
        "syllabus_data": df_data.to_dict('records'), 
        "resources": resources,
        "test_scores": test_scores,
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

# --- IMPROVED PDF PARSER ---
def parse_schedule_pdf(uploaded_file):
    try:
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages: text += page.extract_text()
        
        today = str(date.today())
        
        prompt = f"""
        CONTEXT: Today's date is {today}.
        DOCUMENT: This is a JEE Syllabus Schedule.
        
        TASK 1: Find tasks specifically for TODAY ({today}). Output as short bullet points.
        TASK 2: Scan for upcoming exams (Keywords: WTM, CTM, Grand Test, Exam) in the next 7 days.
        
        OUTPUT FORMAT:
        **TODAY'S MISSIONS:**
        - [Task 1]
        - [Task 2]
        
        **UPCOMING BATTLES:**
        - [Date]: [Exam Name]
        (If none, say "No exams detected.")
        
        Text to analyze: {text[:5000]}
        """
        response = model.generate_content(prompt)
        return response.text
    except: return "Could not parse schedule."

# --- 5. SETUP WIZARD ---
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = load_profile()

if not st.session_state['user_profile']:
    st.title("🚀 INITIALIZATION")
    target_sel = st.selectbox("SELECT GOAL", ["JEE Main 2026", "JEE Advanced 2026", "AP EAPCET 2026"])
    
    if 'wizard_df' not in st.session_state or st.session_state.get('last_wiz_target') != target_sel:
        raw_data = get_syllabus_data(target_sel)
        df_wiz = pd.DataFrame(raw_data)
        df_wiz['Status'] = 'Pending'
        df_wiz['Confidence'] = 0
        df_wiz['Impact_Score'] = 0.0
        st.session_state['wizard_df'] = df_wiz
        st.session_state['last_wiz_target'] = target_sel
        st.rerun()

    st.info("Mark completed chapters.")
    edited_df = st.data_editor(st.session_state['wizard_df'], use_container_width=True, hide_index=True)
    
    if st.button("START DASHBOARD"):
        prof = save_profile(target_sel, edited_df)
        st.session_state['user_profile'] = prof
        st.rerun()

# --- 6. MAIN APPLICATION ---
else:
    profile = st.session_state['user_profile']
    target = profile['target']
    df = pd.DataFrame(profile['syllabus_data'])
    if 'Impact_Score' not in df.columns: df['Impact_Score'] = 0.0
    
    resources = profile.get('resources', [])
    test_scores = profile.get('test_scores', [])
    schedule_text = profile.get('schedule_text', "No schedule uploaded.")
    
    readiness, est_score, target_marks = calculate_metrics(df, target)
    sub_breakdown = get_subject_breakdown(df)

    # SIDEBAR
    with st.sidebar:
        st.title("PROJECT 02")
        
        # THEME TOGGLE
        theme_choice = st.radio("Theme", ["Zero Two (Dark)", "EdTech (Light)"])
        apply_theme(theme_choice)
        
        st.divider()
        uploaded_file = st.file_uploader("Schedule PDF", type="pdf")
        if uploaded_file and api_status:
            if st.button("Scan PDF"):
                with st.spinner("Analyzing..."):
                    schedule_text = parse_schedule_pdf(uploaded_file)
                    save_profile(target, df, resources, schedule_text, test_scores)
                    st.rerun()
        
        if st.button("Reset App"):
            os.remove(PROFILE_FILE)
            st.session_state['user_profile'] = None
            st.rerun()

    # --- MAIN TABS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🏠 HOME", "📊 ANALYTICS", "📝 SYLLABUS", "📚 LIBRARY", "💬 MENTOR"]
    )

    # TAB 1: HOME
    with tab1:
        # Metrics Row
        with st.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("Readiness", f"{readiness}%", "Weighted Score")
            c2.metric("Est. Score", f"{est_score}", f"Goal: {target_marks}")
            c3.metric("System", "Online", "AI Active")
        
        st.divider()
        
        # Split: Schedule vs Logging
        col_sch, col_log = st.columns([1, 1])
        
        with col_sch:
            with st.container():
                st.subheader("📅 Today's Briefing")
                if "WTM" in schedule_text or "CTM" in schedule_text or "Exam" in schedule_text:
                    st.error("⚠️ EXAM DETECTED IN SCHEDULE")
                st.info(schedule_text)
            
        with col_log:
            with st.container():
                st.subheader("⌨️ Log Progress")
                log_in = st.text_area("What did you finish?", placeholder="I mastered Rotational Motion...")
                if st.button("Update Status"):
                    if api_status:
                        ups = ai_process_log(log_in, profile['syllabus_data'])
                        if ups:
                            for u in ups:
                                df.loc[df['Chapter'].str.contains(u['Chapter'], case=False), 'Status'] = u['Status']
                            save_profile(target, df, resources, schedule_text, test_scores)
                            st.success("Updated!")
                            st.rerun()

    # TAB 2: ANALYTICS
    with tab2:
        with st.container():
            st.subheader("🚀 Goal Analysis")
            c1, c2 = st.columns([2, 1])
            with c1:
                # Goal Gap Chart
                gap_fig = go.Figure()
                gap_fig.add_trace(go.Bar(y=['Score'], x=[est_score], name='You', orientation='h', marker_color='#007CF0'))
                gap_fig.add_trace(go.Bar(y=['Score'], x=[target_marks], name=f'Target ({target})', orientation='h', marker_color='#00DFD8', opacity=0.5))
                # Fixed layout syntax
                gap_fig.update_layout(barmode='overlay', height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(gap_fig, use_container_width=True)
            with c2:
                st.warning(f"GAP: {target_marks - est_score} Marks")
                st.write("To reach IIT Hyderabad CSE, focus on High Weightage chapters.")

        st.divider()
        
        with st.container():
            st.subheader("🧠 Subject Strength")
            cp1, cp2, cp3 = st.columns(3)
            def donut(val, color):
                return go.Figure(data=[go.Pie(values=[val, 100-val], hole=.7, marker_colors=[color, '#333'])]).update_layout(showlegend=False, height=120, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            
            with cp1: 
                st.markdown("**Physics**"); st.plotly_chart(donut(sub_breakdown.get("Physics",0), "#007CF0"), use_container_width=True)
            with cp2: 
                st.markdown("**Chemistry**"); st.plotly_chart(donut(sub_breakdown.get("Chemistry",0), "#00DFD8"), use_container_width=True)
            with cp3: 
                st.markdown("**Maths**"); st.plotly_chart(donut(sub_breakdown.get("Maths",0), "#ff003c"), use_container_width=True)

            if st.button("GENERATE STRATEGIC REPORT"):
                if api_status:
                    with st.spinner("Analyzing Codex..."):
                        summary = df.groupby('Subject')['Status'].value_counts().to_json()
                        prompt = f"Analyze progress: {summary}. Goal: {target}. Identify weak subjects. Give 3 specific actionable steps."
                        try:
                            report = model.generate_content(prompt).text
                            st.markdown(f"<div class='report-box'>{report}</div>", unsafe_allow_html=True)
                        except Exception as e: st.error(f"Error: {e}")

    # TAB 3: SYLLABUS
    with tab3:
        with st.container():
            st.subheader("🗂️ Master Codex")
            st.caption("Impact Score = Weightage × Status")
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
                save_profile(target, df, resources, schedule_text, test_scores)
                st.success("Saved!")
                st.rerun()

    # TAB 4: LIBRARY
    with tab4:
        st.subheader("📚 Resources")
        with st.expander("Add New"):
            rn, rl = st.text_input("Title"), st.text_input("URL")
            if st.button("Add"):
                resources.append({"name":rn, "link":rl})
                save_profile(target, df, resources, schedule_text, test_scores)
                st.rerun()
        for r in resources: st.markdown(f"- [{r['name']}]({r['link']})")

    # TAB 5: MENTOR
    with tab5:
        st.subheader("💬 Zero Two")
        q = st.chat_input("Ask strategy...")
        if q and api_status:
            with st.chat_message("user"): st.write(q)
            with st.chat_message("assistant"):
                try:
                    res = model.generate_content(f"Act as academic strategist Zero Two. Goal: {target}. User: {q}")
                    st.write(res.text)
                except: st.error("AI Error")
