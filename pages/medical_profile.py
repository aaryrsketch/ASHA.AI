import streamlit as st
from datetime import date, timedelta
from supabase import create_client

st.set_page_config(layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"],st.secrets["SUPABASE_KEY"])
id=st.session_state["profileid"]
profile=supabase.table("cases").select("*").eq("id",id).execute()
row=profile.data
st.set_page_config(page_title="Initial Medical Registration", layout="centered")
data={}
st.title(f"Medical details of {row[0]["name"]}")
st.caption("Filled by ANM at first contact")
st.divider()
firstinfo=False
if not supabase.table("medical_cases").select("*").eq("id",id).execute().data:
    col1, col2 = st.columns(2)
    with st.form("Medical Details"):
        st.subheader("Physical Profile")

        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age (years)", min_value=10, max_value=60, step=1)
        with col2:
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=150.0, step=0.1)
        with col3:
            height = st.number_input("Height (cm)", min_value=100.0, max_value=200.0, step=0.1)

        col1, col2 = st.columns(2)
        with col1:
            blood_group = st.selectbox("Blood Group", ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        with col2:
            muac = st.number_input("MUAC (cm)", min_value=10.0, max_value=40.0, step=0.1)

        if height > 0 and weight > 0:
            bmi = weight / ((height / 100) ** 2)
            bmi_label = (
                "Underweight" if bmi < 18.5 else
                "Normal" if bmi < 25 else
                "Overweight" if bmi < 30 else "Obese"
            )
            st.caption(f"BMI: {bmi:.1f} — {bmi_label}")

        st.divider()

        st.subheader("Pregnancy Details")

        col1, col2 = st.columns(2)
        with col1:
            lmp = st.date_input("Last Menstrual Period (LMP)",
                                value=date.today() - timedelta(weeks=8),
                                max_value=date.today())
        with col2:
            edd = lmp + timedelta(weeks=40)
            st.date_input("Estimated Due Date (EDD)", value=edd, disabled=True)

        ga_days = (date.today() - lmp).days
        ga_weeks = ga_days // 7
        ga_rem = ga_days % 7
        trimester = (
            1 if ga_weeks <= 12 else
            2 if ga_weeks <= 26 else
            3
        )
        trimester_label = {1: "1st Trimester", 2: "2nd Trimester", 3: "3rd Trimester"}[trimester]
        st.caption(f"Gestational Age: {ga_weeks} weeks {ga_rem} days — {trimester_label}")

        st.divider()

        st.subheader("Obstetric History")

        col1, col2, col3 = st.columns(3)
        with col1:
            gravida = st.number_input("Gravida", min_value=1, step=1)
        with col2:
            para = st.number_input("Para", min_value=0, step=1)
        with col3:
            abortions = st.number_input("Abortions / Miscarriages", min_value=0, step=1)

        
        col1, col2 = st.columns(2)
        with col1:
                last_outcome = st.selectbox("Last Pregnancy Outcome",
                    ["Normal", "C-Section",
                    "Stillbirth", "Abortion"])
                last_birth_weight = st.number_input("Last Baby Birth Weight (kg)",
                                                    min_value=0.5, max_value=6.0, step=0.1)
        with col2:
                inter_pregnancy = st.number_input("Inter-pregnancy Interval (months)",
                                                min_value=0, max_value=240, step=1)
                bad_obstetric = st.checkbox("Bad Obstetric History (BOH)")

        if last_outcome in ["Stillbirth", "Neonatal death"] or bad_obstetric:
                st.warning("Bad obstetric history — high risk")
        if inter_pregnancy > 0 and inter_pregnancy < 18:
                st.warning("Inter-pregnancy interval <18 months")

        st.divider()

        st.subheader("Vitals at Registration")

        col1, col2, col3 = st.columns(3)
        with col1:
            bp_sys = st.number_input("BP Systolic (mmHg)", min_value=60, max_value=220, step=1)
            bp_dia = st.number_input("BP Diastolic (mmHg)", min_value=40, max_value=140, step=1)
        with col2:
            hb = st.number_input("Haemoglobin (g/dL)", min_value=3.0, max_value=20.0, step=0.1)
            heart_rate = st.number_input("Heart Rate (bpm)", min_value=40, max_value=180, step=1)
        with col3:
            temp = st.number_input("Temperature (F)", min_value=95.0, max_value=106.0, step=0.1)
            blood_sugar = st.number_input("Blood Sugar Random (mg/dL)", min_value=0, max_value=500, step=1)

        urine_albumin = st.radio("Urine Albumin", ["Nil", "1+", "2+", "3+"], horizontal=True)
        urine_sugar = st.radio("Urine Sugar", ["Nil", "1+", "2+"], horizontal=True)

        st.divider()

        st.subheader("Immunisation and Medication")

        col1, col2 = st.columns(2)
        with col1:
            tt_status = st.selectbox("TT Immunisation Status",
                ["Not given", "TT1 given", "TT2 given", "Booster given", "Previously protected"])
            if "given" in tt_status:
                tt_date = st.date_input("TT Date", value=date.today())
        with col2:
            ifa_given = st.checkbox("IFA Tablets Given",)
            calcium_given = st.checkbox("Calcium Tablets Given")

        st.divider()

        st.subheader("Medical and Family History")

        col1, col2 = st.columns(2)
        with col1:
            st.caption("Pre-existing Conditions")
            diabetes = st.checkbox("Diabetes")
            hypertension = st.checkbox("Hypertension")
            thyroid = st.checkbox("Thyroid disorder")
            epilepsy = st.checkbox("Epilepsy / Seizures")
            hiv = st.checkbox("HIV positive")
            sickle_cell = st.checkbox("Sickle cell / Thalassaemia")
            other_condition = st.text_input("Other condition")
        with col2:
            st.caption("Family History")
            fam_twins = st.checkbox("Twins in family")
            fam_diabetes = st.checkbox("Diabetes in family")
            fam_hypertension = st.checkbox("Hypertension in family")
            fam_genetic = st.checkbox("Genetic / Congenital conditions")

       
        st.divider()

        # SECTION 8: SOCIOECONOMIC CONTEXT
        st.subheader("Socioeconomic Context")

        col1, col2 = st.columns(2)
        with col1:
            distance_phc = st.number_input("Distance to nearest PHC (km)", min_value=0.0, step=0.5)
            transport = st.radio("Emergency transport available", ["Yes", "No", "Uncertain"], horizontal=True)
            toilet = st.radio("Toilet facility at home", ["Yes", "No"], horizontal=True)
        with col2:
            literacy = st.selectbox("Mother's literacy",
                ["Illiterate", "Can read only", "Primary", "Secondary", "Graduate+"])
            husband_occupation = st.selectbox("Husband's occupation",
                ["Daily wage labour", "Farmer", "Salaried", "Business", "Migrant worker", "Unemployed", "Other"])
            meals_per_day = st.radio("Meals per day", ["1", "2", "3", "3+"], horizontal=True)

        st.divider()

        # SECTION 9: ANM ASSESSMENT
        st.subheader("ANM Assessment")

        
        referral_needed = st.radio("Referral needed", ["No", "Yes — PHC", "Yes — CHC/Hospital"], horizontal=True)
        if referral_needed != "No":
            referral_reason = st.text_area("Reason for referral")

        anm_notes = st.text_area("ANM Notes", height=100)
        supervisor_flag = st.checkbox("Flag for supervisor review")
        st.space(size="small")
        submit=st.form_submit_button("submit details")
    if submit==True:
        data = {
            "id": id,
            "name": row[0]["name"],
            "age": age,
            "weight": weight,
            "height": height,
            "blood_group": blood_group,
            "muac": muac,
            "bmi": round(bmi, 1) if height > 0 and weight > 0 else None,

            "lmp": str(lmp),
            "edd": str(edd),
            "ga_weeks": ga_weeks,
            "ga_rem": ga_rem,
            "trimester": trimester,

            "gravida": gravida,
            "para": para,
            "abortions": abortions,
            "last_outcome": last_outcome if gravida > 1 else None,
            "last_birth_weight": last_birth_weight if gravida > 1 else None,
            "inter_pregnancy": inter_pregnancy if gravida > 1 else None,
            "bad_obstetric": bad_obstetric if gravida > 1 else None,

            "bp_sys": bp_sys,
            "bp_dia": bp_dia,
            "hb": hb,
            "heart_rate": heart_rate,
            "temp": temp,
            "blood_sugar": blood_sugar if blood_sugar > 0 else None,
            "urine_albumin": urine_albumin,
            "urine_sugar": urine_sugar,

            "tt_status": tt_status,
            "tt_date": str(tt_date) if "given" in tt_status and tt_date else None,

            "ifa_given": ifa_given,
            "calcium_given": calcium_given,

            "diabetes": diabetes,
            "hypertension": hypertension,
            "thyroid": thyroid,
            "epilepsy": epilepsy,
            "hiv": hiv,
            "sickle_cell": sickle_cell,
            "other_condition": other_condition if other_condition else None,

            "fam_twins": fam_twins,
            "fam_diabetes": fam_diabetes,
            "fam_hypertension": fam_hypertension,
            "fam_genetic": fam_genetic,

            "distance_phc": distance_phc,
            "transport": transport,
            "toilet": toilet,
            "literacy": literacy,
            "husband_occupation": husband_occupation,
            "meals_per_day": meals_per_day,

            
            "referral_needed": referral_needed,
            "referral_reason": referral_reason if referral_needed != "No" else None,
            "anm_notes": anm_notes if anm_notes else None,
            "supervisor_flag": supervisor_flag
        }
        response=supabase.table("medical_cases").insert(data).execute()
medidate=supabase.table("cases").select("*").eq("id",id).execute().data[0]