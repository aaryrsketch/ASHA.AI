import streamlit as st
import joblib
from supabase import create_client
from pages.ai_response import risk_report
from pages.golssary import medical_glossary 
from pages.golssary import social_glossary
from pages.ml import predict_risk
from pages.ai_chatbot import query_answer
st.set_page_config(layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"],st.secrets["SUPABASE_KEY"])
profileid=st.session_state["profileid"]
profile=supabase.table("cases").select("*").eq("id",profileid).execute()
model = joblib.load('pages/asha_risk_model.pkl')
row=profile.data
profinfo=row[0]
medprofile=supabase.table("medical_cases").select("*").eq("id",profileid).execute().data[0]

from datetime import date, datetime, timedelta

p = profile.data[0]

lmp = datetime.strptime(p["lmp"], "%Y-%m-%d").date()
gest_weeks = (date.today() - lmp).days // 7
edd = lmp + timedelta(days=280)
progress_val = min((date.today() - lmp).days / 280, 1.0)

# --- Avatar + name ---
st.markdown(f"""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:1rem">
  <div style="width:52px;height:52px;border-radius:50%;background:#E1F5EE;display:flex;
    align-items:center;justify-content:center;font-size:20px;font-weight:500;color:#0F6E56">
    {p['name'][0].upper()}
  </div>
  <div>
    <div style="font-size:22px;font-weight:600">{p['name']}</div>
    <div style="font-size:13px;color:gray">{p['age']} yrs · {p['caste']} · {p['village']}, {p['district'].title()}, {p['state'].title()}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# --- Risk pills ---
def pill(text, color):
    colors = {
        "red":   ("#F79797","#A32D2D"),
        "amber": ("#F7DBAB","#854F0B"),
        "green": ("#CBF496","#3B6D11"),
    }
    bg, fg = colors[color]
    return f'<span style="background:{bg};color:{fg};padding:3px 10px;border-radius:20px;font-size:12px;font-weight:500;margin-right:4px">{text}</span>'

flags_html = ""
if "High BP/Preclampsia" in p["complications"]:
    flags_html += pill("⚠ High BP history", "red")
if "C-section" in p["complications"]:
    flags_html += pill("C-section history", "amber")
if not p["jsy"]:
    flags_html += pill("JSY not registered", "amber")
if p["adahaar"]:
    flags_html += pill("✓ Aadhaar", "green")

st.markdown(flags_html, unsafe_allow_html=True)

tab4,tab5,tab8=st.tabs(["Profile info","Ai report","AI Chat Bot"])
with tab4:
    #col_prog, col_edd = st.columns([3, 1])
    #col_prog.caption(f"Pregnancy progress · LMP {lmp.strftime('%d %b %Y')}")
    #col_prog.progress(progress_val)
    #col_edd.markdown(f"**Week {gest_weeks}**  \n{edd.strftime('%d %b %Y')}")

    # --- Section helper ---
    def kv_grid(items):
        cols = st.columns(len(items))
        for col, (label, val, color) in zip(cols, items):
            color_map = {"green": "#E68080", "red": "#A32D2D", None: "inherit"}
            c = color_map.get(color, "inherit")
            col.markdown(f"""
            <div style="background:var(--secondary-background-color);border-radius:8px;padding:10px 12px">
            <div style="font-size:11px;color:gray;margin-bottom:3px">{label}</div>
            <div style="font-size:14px;font-weight:600;color:{c}">{val}</div>
            </div>""", unsafe_allow_html=True)

    # --- Personal ---
    st.markdown("#### Personal")
    kv_grid([
        ("Contact", p["contact_no"], None),
        ("Phone", p["phone"].title(), None),
        ("Education", p["edu"].title(), None),
        ("Can read", "Yes" if p["read"] else "No", "green" if p["read"] else "red"),
        ("Knows warning signs", "Yes" if p["warn"] else "No", "green" if p["warn"] else "red"),
    ])

    # --- Obstetric history ---
    st.markdown("#### Obstetric history")
    kv_grid([
        ("Prev. pregnancies", p["no_preg"], None),
        ("Live births", p["livebirth"], None),
        ("Miscarriage", "None" if not p["miscarriage"] else "Yes", "green" if not p["miscarriage"] else "red"),
        ("Past delivery", p["delivery"].title(), None),
    ])
    comp_pills = " ".join([pill(c, "red" if "BP" in c else "amber") for c in p["complications"]])
    st.markdown(comp_pills, unsafe_allow_html=True)

    # --- Household ---
    st.markdown("#### Household & support")
    rows = [
        ("Primary support", p["prime_support"]),
        ("Female support", p["female_support"].title()),
        ("Health decision maker", p["prime_decider"]),
        ("Can go to PHC", "Yes" if p["access_person"] else "No"),
        ("Family members", p["family_no"]),
    ]
    for label, val in rows:
        c1, c2 = st.columns([2, 1])
        c1.caption(label)
        c2.markdown(f"**{val}**")

    # --- Economic ---
    st.markdown("#### Economic & access")
    kv_grid([
        ("Income source", p["pi_source"].title(), None),
        ("Monthly income", f"₹{p['monthly_income']:,}", None),
        ("Works physically", p["does_she_work"], None),
        ("Distance to PHC", f"{p['distance_phc']} km", None),
        ("Transport", p["transport"].title(), None),
    ])

    # --- Schemes ---
    st.markdown("#### Scheme eligibility")
    sc1, sc2, sc3 = st.columns(3)
    sc1.markdown(pill("✓ Aadhaar" if p["adahaar"] else "✗ Aadhaar", "green" if p["adahaar"] else "red"), unsafe_allow_html=True)
    sc2.markdown(pill("✓ JSY" if p["jsy"] else "✗ JSY not registered", "green" if p["jsy"] else "amber"), unsafe_allow_html=True)
    sc3.markdown(pill("✓ Jan Dhan" if p["jan_dhan"] else "✗ No Jan Dhan", "green" if p["jan_dhan"] else "amber"), unsafe_allow_html=True)

    def display_medical_profile(medprofile):
        m = medprofile

        def row(col, label, value):
            col.caption(label)
            col.write(value if value not in [None, "", 0] else "—")

        st.title("Medical Profile")
        st.caption(f"Patient ID: {m.get('id', 'N/A')}")

        # --- BASIC INFO ---
        st.subheader("Basic Information")
        c1, c2, c3, c4 = st.columns(4)
        row(c1, "Age", f"{m.get('age')} yrs")
        row(c2, "Blood Group", m.get("blood_group"))
        row(c3, "BMI", m.get("bmi"))
        row(c4, "MUAC", f"{m.get('muac')} cm")

        c1, c2 = st.columns(2)
        row(c1, "Weight", f"{m.get('weight')} kg")
        row(c2, "Height", f"{m.get('height')} cm")

        st.divider()

        # --- PREGNANCY ---
        st.subheader("Pregnancy")
        c1, c2, c3, c4 = st.columns(4)
        row(c1, "Gestational Age", f"{m.get('ga_weeks')}w {m.get('ga_rem')}d")
        row(c2, "Trimester", m.get("trimester"))
        row(c3, "LMP", str(m.get("lmp") or "—"))
        row(c4, "EDD", str(m.get("edd") or "—"))

        st.divider()

        # --- OBSTETRIC HISTORY ---
        st.subheader("Obstetric History")
        c1, c2, c3 = st.columns(3)
        row(c1, "Gravida", m.get("gravida"))
        row(c2, "Para", m.get("para"))
        row(c3, "Abortions", m.get("abortions"))

        if m.get("gravida", 1) > 1:
            c1, c2, c3, c4 = st.columns(4)
            row(c1, "Last Outcome", m.get("last_outcome"))
            row(c2, "Last Birth Weight", f"{m.get('last_birth_weight')} kg")
            row(c3, "Inter-Pregnancy Gap", f"{m.get('inter_pregnancy')} months")
            row(c4, "Bad Obstetric History", "Yes" if m.get("bad_obstetric") else "No")

        st.divider()

        # --- VITALS ---
        st.subheader("Current Vitals")
        c1, c2, c3, c4 = st.columns(4)
        row(c1, "Blood Pressure", f"{m.get('bp_sys')}/{m.get('bp_dia')} mmHg")
        row(c2, "Hemoglobin", f"{m.get('hb')} g/dL")
        row(c3, "Heart Rate", f"{m.get('heart_rate')} bpm")
        row(c4, "Temperature", f"{m.get('temp')} °F")

        c1, c2, c3 = st.columns(3)
        row(c1, "Blood Sugar", f"{m.get('blood_sugar')} mg/dL" if m.get("blood_sugar") else "Not tested")
        row(c2, "Urine Albumin", m.get("urine_albumin"))
        row(c3, "Urine Sugar", m.get("urine_sugar"))

        st.divider()

        # --- IMMUNIZATION & SUPPLEMENTS ---
        st.subheader("Immunization & Supplements")
        c1, c2, c3, c4 = st.columns(4)
        row(c1, "TT Status", m.get("tt_status"))
        row(c2, "TT Date", str(m.get("tt_date") or "—"))
        row(c3, "IFA Given", "Yes" if m.get("ifa_given") else "No")
        row(c4, "Calcium Given", "Yes" if m.get("calcium_given") else "No")

        st.divider()

        # --- MEDICAL CONDITIONS ---
        st.subheader("Medical Conditions")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        row(c1, "Diabetes", "Yes" if m.get("diabetes") else "No")
        row(c2, "Hypertension", "Yes" if m.get("hypertension") else "No")
        row(c3, "Thyroid", "Yes" if m.get("thyroid") else "No")
        row(c4, "Epilepsy", "Yes" if m.get("epilepsy") else "No")
        row(c5, "HIV", "Yes" if m.get("hiv") else "No")
        row(c6, "Sickle Cell", "Yes" if m.get("sickle_cell") else "No")

        if m.get("other_condition"):
            st.caption("Other Condition")
            st.write(m["other_condition"])

        st.divider()

        # --- FAMILY HISTORY ---
        st.subheader("Family History")
        c1, c2, c3, c4 = st.columns(4)
        row(c1, "Twins", "Yes" if m.get("fam_twins") else "No")
        row(c2, "Diabetes", "Yes" if m.get("fam_diabetes") else "No")
        row(c3, "Hypertension", "Yes" if m.get("fam_hypertension") else "No")
        row(c4, "Genetic Disorders", "Yes" if m.get("fam_genetic") else "No")

        st.divider()

        # --- SOCIAL FACTORS ---
        st.subheader("Social Factors")
        c1, c2, c3, c4 = st.columns(4)
        row(c1, "Distance to PHC", f"{m.get('distance_phc')} km")
        row(c2, "Transport", m.get("transport"))
        row(c3, "Toilet Access", m.get("toilet"))
        row(c4, "Literacy", m.get("literacy"))

        c1, c2 = st.columns(2)
        row(c1, "Husband's Occupation", m.get("husband_occupation"))
        row(c2, "Meals per Day", m.get("meals_per_day"))

        st.divider()

        # --- RISK & REFERRAL ---
        st.subheader("Risk & Referral")
        c1, c2, c3 = st.columns(3)
        row(c1, "Risk Level", m.get("risk_level"))
        row(c2, "Referral Needed", m.get("referral_needed"))
        row(c3, "Supervisor Flag", "Yes" if m.get("supervisor_flag") else "No")

        if m.get("referral_reason"):
            st.caption("Referral Reason")
            st.write(m["referral_reason"])
        if m.get("anm_notes"):
            st.caption("ANM Notes")
            st.write(m["anm_notes"])
    st.write("---")
    display_medical_profile(medprofile)
    st.write("---")
    if st.button("back to Dashboard"):
        st.switch_page("pages/profiles_page.py")

    
with tab5:
   
    st.title("AI REPORT")
    st.text("The system provided below is an AI-powered decision support tool that analyzes a mother’s medical and social profile to generate a comprehensive risk assessment report. It uses a trained Random Forest machine learning model to evaluate multiple input features such as health indicators, clinical history, and social determinants of health.The model processes structured patient data and predicts the risk level (e.g., low, moderate, high risk) based on learned patterns from historical datasets. Random Forest is used due to its robustness, ability to handle mixed-type features, and strong performance on classification tasks in healthcare domains.")
    if st.button("Generate report"):
        with st.spinner("please wait while we generate a report"):
            risk_level,mldata = predict_risk(medprofile)
            medprofile['risk_level'] = risk_level
            risk=risk_report(medprofile,medical_glossary,p,social_glossary,risk_level)
        col1,col2,col3=st.columns(3)
        with col1:
            st.metric("Social Risk",risk["social_risk"])
        st.subheader("Social report summary")
        st.text(risk["social_description"])
        with col2:
            st.metric("Medical Risk ",risk_level)
        st.space("small")
        st.subheader("medical report summary")
        st.text(risk["medical_description"])
        with col3:
            st.metric("overall Risk",risk["overall_risk"])
        st.space("small")
        st.subheader("overall report summary")
        st.text(risk["overall_description"])
        st.subheader("useful tips and advice")
        st.text(risk["advice_tips"])
        st.write("---")


        
with tab8:
    st.title("Hi...my name is ASHA.AI !!")
    st.text("Im your personal health care companion. I’m here to support you with gentle, reliable guidance for pregnancy, motherhood, child care, family health, nutrition, emotional well-being, and social support.")
    st.text("I will always respond with care, patience, and respect. My goal is to help you feel informed, supported, and confident while guiding you toward proper medical care whenever needed.You are not alone — I’m here to listen, guide, and support you with kindness and care")
    query=st.chat_input("ask me anything")
    if st.button("answer"):
        answer=query_answer(medprofile,medical_glossary,p,social_glossary,query)
        st.text(answer["answer"])