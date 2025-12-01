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
            .stApp { background-color: #050505; }
            h1, h2, h3 { 
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
        </style>
        """, unsafe_allow_html=True)
    else:
        # EDTECH (Byju's/nLearn Style) - WHITE & BLUE
        st.markdown("""
        <style>
            .stApp { background-color: #f4f7f6; }
            h1, h2, h3 { 
                color: #2d3436;
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
                box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: none;
            }
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
    
    # Universal Model Finder
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
    # Logic: High=3pts, Avg=2pts, Low=1pt
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
    
    # Goal Logic
    total_marks = 300 if "JEE" in target_exam else 160
    target_marks = 240 if "JEE" in target_exam else 130
    est_score = int(total_marks * (readiness / 100))
    
    # Rank/Percentile Prediction
    if "JEE" in target_exam:
        if est_score > 250: est_rank = "< 500 (99.9%ile)"
        elif est_score > 200: est_rank = "< 2,000 (99.5%ile)"
        elif est_score > 150: est_rank = "< 10,000 (97%ile)"
        else: est_rank = "> 20,000"
    else:
        est_rank = f"Rank Est: {int(50000 * (1 - readiness/100))}"
        
    return readiness, est_score, target_marks, est_rank

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

def parse_schedule_pdf(uploaded_file):
    try:
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages: text += page.extract_text()
        prompt = f"Find exams and key topics in this text for the next 7 days. Summarize briefly. Text: {text[:3000]}"
        response = model.generate_content(prompt)
        return response.text
    except: return "Could not parse schedule."

# --- 5. SETUP WIZARD (First Time) ---
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
        df_wiz['Impact_Score'] = 0.0 # Init column
        st.session_state['wizard_df'] = df_wiz
        st.session_state['last_wiz_target'] = target_sel
        st.rerun()

    st.info("Mark completed chapters. (Use the Dashboard later for detailed editing)")
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
    if 'Impact_Score' not in df.columns: df['Impact_Score'] = 0.0 # Safe fallback
    
    resources = profile.get('resources', [])
    test_scores = profile.get('test_scores', [])
    schedule_text = profile.get('schedule_text', "No schedule uploaded.")
    
    readiness, est_score, target_marks, est_rank = calculate_metrics(df, target)
    sub_breakdown = get_subject_breakdown(df)

    # SIDEBAR
    with st.sidebar:
        st.title("PROJECT 02")
        st.caption("ARCHITECT: SRIRAM")
        
        # THEME TOGGLE
        theme_choice = st.radio("Theme", ["Zero Two (Dark)", "EdTech (Light)"])
        apply_theme(theme_choice)
        
        st.divider()
        uploaded_file = st.file_uploader("Schedule PDF", type="pdf")
        if uploaded_file and api_status:
            if st.button("Scan PDF"):
                with st.spinner("Scanning..."):
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

    # TAB 1: HOME (Daily Ops)
    with tab1:
        # Top Metrics
        with st.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("Readiness", f"{readiness}%", "Weighted")
            c2.metric("Est. Rank", est_rank, f"Goal: {target_marks} Marks")
            c3.metric("Status", "Online", status_msg)
        
        st.divider()
        
        col_sch, col_log = st.columns([1, 1])
        
        with col_sch:
            st.subheader("📅 Today's Schedule")
            st.info(schedule_text)
            
        with col_log:
            st.subheader("⌨️ Log Progress")
            log_in = st.text_area("What did you finish today?", placeholder="I finished Rotational Motion revision...")
            if st.button("Update Status"):
                if api_status:
                    ups = ai_process_log(log_in, profile['syllabus_data'])
                    if ups:
                        for u in ups:
                            df.loc[df['Chapter'].str.contains(u['Chapter'], case=False), 'Status'] = u['Status']
                        save_profile(target, df, resources, schedule_text, test_scores)
                        st.success("Updated!")
                        st.rerun()

    # TAB 2: ANALYTICS (Graphs)
    with tab2:
        st.subheader("🚀 Goal Analysis")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            # GOAL GAP CHART
            gap_fig = go.Figure()
            gap_fig.add_trace(go.Bar(y=['Score'], x=[est_score], name='Current', orientation='h', marker_color='#007CF0'))
            gap_fig.add_trace(go.Bar(y=['Score'], x=[target_marks], name=f'Target ({target})', orientation='h', marker_color='#00DFD8', opacity=0.5))
            gap_fig.update_layout(barmode='overlay', height=250, bg_color='rgba(0,0,0,0)')
            st.plotly_chart(gap_fig, use_container_width=True)
            
        with c2:
            st.warning(f"GAP: {target_marks - est_score} Marks")
            st.write("Improvement needed to reach IIT Hyderabad CSE cutoff.")

        st.divider()
        st.subheader("🧠 Subject Strength")
        
        cp1, cp2, cp3 = st.columns(3)
        def donut(val, color):
            return go.Figure(data=[go.Pie(values=[val, 100-val], hole=.7, marker_colors=[color, '#333'])]).update_layout(showlegend=False, height=120, margin=dict(t=0,b=0,l=0,r=0))
        
        with cp1: 
            st.write("Physics"); st.plotly_chart(donut(sub_breakdown.get("Physics",0), "#007CF0"), use_container_width=True)
        with cp2: 
            st.write("Chemistry"); st.plotly_chart(donut(sub_breakdown.get("Chemistry",0), "#00DFD8"), use_container_width=True)
        with cp3: 
            st.write("Maths"); st.plotly_chart(donut(sub_breakdown.get("Maths",0), "#ff003c"), use_container_width=True)

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
