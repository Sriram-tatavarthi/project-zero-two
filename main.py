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
st.set_page_config(page_title="Project Zero Two: MK XVI", page_icon="logo.jpg", layout="wide")

# --- 2. PROFESSIONAL EDTECH THEME ---
st.markdown("""
<style>
    /* Global Background */
    .stApp { background-color: #0e1117; }
    
    /* Gradient Headers */
    h1, h2, h3 { 
        background: -webkit-linear-gradient(0deg, #007CF0, #00DFD8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 26px; color: #007CF0; font-weight: bold;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid #333; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; font-weight: 600; color: #888;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #007CF0; border-bottom: 3px solid #007CF0;
    }
    
    /* AI Report Box */
    .report-box {
        padding: 20px; border-radius: 10px; background: rgba(0, 124, 240, 0.1);
        border-left: 5px solid #007CF0; margin-top: 20px;
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
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_status = True
    else:
        api_status = False
except:
    api_status = False

def calculate_metrics(df, target_exam):
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
    readiness = int((earned/total)*100) if total > 0 else 0
    
    total_marks = 300 if "JEE" in target_exam else 160
    target_marks = 240 if "JEE" in target_exam else 130
    est_score = int(total_marks * (readiness / 100))
    
    if "JEE" in target_exam:
        if est_score > 250: est_perc = "99.9%ile"
        elif est_score > 200: est_perc = "99.5%ile"
        elif est_score > 150: est_perc = "97.0%ile"
        else: est_perc = "< 90%ile"
    else:
        est_perc = "N/A (Rank Based)"
        
    return readiness, est_score, target_marks, est_perc

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
    prompt = f"Analyze: '{text}'. Match to: {valid_chaps}. Return JSON: [{{'Chapter': 'Name', 'Status': 'Mastered'}}]"
    try:
        response = model.generate_content(prompt)
        clean = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except: return []

# --- 5. SETUP WIZARD ---
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = load_profile()

if not st.session_state['user_profile']:
    st.title("🚀 SYSTEM INITIALIZATION")
    target_sel = st.selectbox("Select Goal", ["JEE Main 2026", "JEE Advanced 2026", "AP EAPCET 2026"])
    
    if 'wizard_df' not in st.session_state or st.session_state.get('last_wiz_target') != target_sel:
        raw_data = get_syllabus_data(target_sel)
        df_wiz = pd.DataFrame(raw_data)
        df_wiz['Status'] = 'Pending'
        df_wiz['Confidence'] = 0
        st.session_state['wizard_df'] = df_wiz
        st.session_state['last_wiz_target'] = target_sel
        st.rerun()

    st.info("Mark your completed chapters to begin.")
    edited_df = st.data_editor(st.session_state['wizard_df'], use_container_width=True, hide_index=True)
    
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
    test_scores = profile.get('test_scores', [])
    schedule_text = profile.get('schedule_text', "No schedule uploaded.")
    
    readiness, est_score, target_marks, est_perc = calculate_metrics(df, target)
    sub_breakdown = get_subject_breakdown(df)

    # SIDEBAR (TEXT ONLY)
    with st.sidebar:
        st.title("PROJECT 02")
        st.caption(f"GOAL: {target}")
        if st.button("Change Goal"):
            os.remove(PROFILE_FILE)
            st.session_state['user_profile'] = None
            st.rerun()
        st.divider()
        uploaded_file = st.file_uploader("Upload Schedule (PDF)", type="pdf")

    # --- MAIN TABS ---
    tab_dash, tab_pred, tab_analy, tab_test, tab_syll, tab_lib, tab_ai = st.tabs(
        ["DASHBOARD", "PREDICTIONS", "ANALYTICS", "TEST CENTER", "SYLLABUS", "LIBRARY", "ZERO TWO"]
    )

    # TAB 1: DASHBOARD
    with tab_dash:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Readiness", f"{readiness}%", "Weighted")
        c2.metric("Est. Score", f"{est_score}", f"Target: {target_marks}")
        c3.metric("Percentile", est_perc, "Predicted")
        c4.metric("Status", "Online", "AI Active" if api_status else "Offline")
        
        st.divider()
        col_sch, col_cmd = st.columns([1,1])
        with col_sch:
            st.subheader("📅 Active Schedule")
            if schedule_text: st.info(schedule_text)
        with col_cmd:
            st.subheader("⌨️ Command Log")
            log_in = st.text_area("Log Input", placeholder="I finished Kinematics...")
            if st.button("Update"):
                if api_status:
                    ups = ai_process_log(log_in, profile['syllabus_data'])
                    if ups:
                        for u in ups:
                            df.loc[df['Chapter'].str.contains(u['Chapter'], case=False), 'Status'] = u['Status']
                        save_profile(target, df, resources, schedule_text, test_scores)
                        st.success("Updated!")
                        st.rerun()

    # TAB 2: PREDICTIONS
    with tab_pred:
        st.subheader("🚀 Goal Gap Analysis")
        c1, c2 = st.columns([2, 1])
        with c1:
            gap_fig = go.Figure()
            gap_fig.add_trace(go.Bar(
                y=['Score'], x=[est_score], name='You', orientation='h', marker_color='#007CF0'
            ))
            gap_fig.add_trace(go.Bar(
                y=['Score'], x=[target_marks], name='IIT Hyderabad', orientation='h', marker_color='#00DFD8', opacity=0.5
            ))
            gap_fig.update_layout(title="You vs IIT Hyderabad Cutoff", barmode='overlay', height=250)
            st.plotly_chart(gap_fig, use_container_width=True)
        with c2:
            st.warning(f"GAP: {target_marks - est_score} Marks")

    # TAB 3: ANALYTICS (FIXED DEEP SCAN)
    with tab_analy:
        st.subheader("🧠 Deep Analysis")
        # Donut Charts
        c_p1, c_p2, c_p3 = st.columns(3)
        def make_donut(val, color):
            fig = go.Figure(data=[go.Pie(labels=['Done', 'Left'], values=[val, 100-val], hole=.7, marker_colors=[color, '#eee'])])
            fig.update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=140)
            return fig
        with c_p1:
            st.write("Physics")
            st.plotly_chart(make_donut(sub_breakdown.get("Physics",0), "#007CF0"), use_container_width=True)
        with c_p2:
            st.write("Chemistry")
            st.plotly_chart(make_donut(sub_breakdown.get("Chemistry",0), "#00DFD8"), use_container_width=True)
        with c_p3:
            st.write("Maths")
            st.plotly_chart(make_donut(sub_breakdown.get("Maths",0), "#7928CA"), use_container_width=True)

        if st.button("INITIALIZE DEEP SCAN"):
            if api_status:
                with st.spinner("Scanning Syllabus Matrix..."):
                    # CRASH FIX: Send Summary JSON, NOT raw text
                    summary_json = df.groupby('Subject')['Status'].value_counts().to_json()
                    prompt = f"Analyze progress: {summary_json}. Goal: {target}. Identify weak subjects and give 3 strategic actions."
                    try:
                        report = model.generate_content(prompt).text
                        st.success("Report Generated")
                        st.markdown(f"<div class='report-box'>{report}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Scan failed: {e}")

    # TAB 4: TEST CENTER
    with tab_test:
        st.subheader("📝 Mock Test Logs")
        with st.expander("Log New Score"):
            t_date = st.date_input("Date")
            t_score = st.number_input("Score", 0, 360)
            t_type = st.selectbox("Type", ["Part Test", "Full Mock"])
            if st.button("Save Score"):
                test_scores.append({"date": str(t_date), "score": t_score, "type": t_type})
                save_profile(target, df, resources, schedule_text, test_scores)
                st.rerun()
        if test_scores:
            ts_df = pd.DataFrame(test_scores)
            st.line_chart(ts_df.set_index('date')['score'])

    # TAB 5: SYLLABUS
    with tab_syll:
        st.subheader("🗂️ Codex")
        sub = st.selectbox("Filter", ["Physics", "Chemistry", "Maths"])
        ed_df = st.data_editor(
            df[df['Subject'] == sub], 
            use_container_width=True,
            column_config={"Status": st.column_config.SelectboxColumn("Status", options=["Pending", "Revision 1", "Revision 2", "Mastered"])}
        )

    # TAB 6: LIBRARY
    with tab_lib:
        st.subheader("📚 Resources")
        with st.expander("Add"):
            r_n = st.text_input("Name")
            r_l = st.text_input("Link")
            if st.button("Add Resource"):
                resources.append({"name":r_n, "link":r_l})
                save_profile(target, df, resources, schedule_text, test_scores)
                st.rerun()
        for r in resources: st.markdown(f"- [{r['name']}]({r['link']})")

    # TAB 7: ZERO TWO
    with tab_ai:
        st.subheader("💬 Zero Two")
        q = st.chat_input("Ask strategy...")
        if q and api_status:
            with st.chat_message("user"): st.write(q)
            with st.chat_message("assistant"):
                res = model.generate_content(f"Act as academic advisor Zero Two. Goal: {target}. User: {q}")
                st.write(res.text)
