import streamlit as st
from supabase import create_client
import datetime

supabase = create_client(st.secrets["SUPABASE_URL"],st.secrets["SUPABASE_KEY"])
st.set_page_config(layout="wide")
st.title("New Profile...")
st.markdown("carefully fill the given details below during the first visit and inform the mother to visit the ANC or primary Healthcare center")
with st.form("Personal details.."):
    st.subheader("Personal Details")
    name=st.text_input("Name:")
    age=st.number_input("Age:",min_value=14,value=18,step=1)
    state=st.selectbox("State present in?",("andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal"))
    district=st.text_input("district")
    ward=st.text_input("ward")
    village=st.text_input("village")
    phone=st.selectbox("phone present?",("cellphone","touchscreen","not present"))    
    contact_no=st.text_input("phone Number")   
    caste=st.selectbox("caste classification (for scheme elegibility and systemic risk assessment)",("SC","ST","OBC","General"))
    jsy=st.checkbox("Registered under JSY")
    jan_dhan=st.checkbox("Has Jan Dhan account")
    adahaar=st.checkbox("Has adahaar account")
    st.write("---")

    st.subheader("Pregnancy and biological history")
    no_preg=st.slider("Number of previous pregnancies",min_value=0,max_value=12,step=1)
    livebirth=st.slider("Live Births",min_value=0,max_value=12)
    miscarriage=st.checkbox("Any miscarriage")
    complications=st.multiselect("Any complications During any births..",["miscarriages","stillbirths","C-section","haemorrhage","High BP/Preclampsia","Fits/Eclampsia","Gestational Diabetes","anemia","infections"])
    lmp=st.date_input("LMP (Last Menstrual Period)")
    lmp=str(lmp)
    delivery=st.selectbox("delivery location",("Homebirth (with midwife)","Homebirth (without midwife or support)","hospital"))
    st.write("---")

    st.subheader("Family details")
    husband=st.checkbox("husband/partner present and active")
    prime_support=st.selectbox("primary support person",("Husband","Non-Spousal Family","not present"))
    family_no=st.slider("Number of primary family members",min_value=0,max_value=12,step=1)
    female_support=st.selectbox("Female support person at home",("none","mother-in-law","sister","mother","daughter(older than 18)"))
    access_person=st.checkbox("can anyone accompany her to the hospital or PHC")
    prime_decider=st.selectbox("Who makes health decisions in the household",("Herself","husband","in-laws",))
    edu=st.selectbox("education level",("no schooling", "primary", "secondary", "graduate+"))
    read=st.checkbox("can she read?")
    warn=st.checkbox("Does she understand the warning signs of pregnancy complications")
    st.write("---")

    st.subheader("Economic Details")
    pi_source=st.selectbox("Primary income source",("daily wage","farming","salaried","other"))
    monthly_income=st.number_input("monthly income(₹)",min_value=1000,max_value=200000,step=1000)
    does_she_work=st.selectbox("does the mother work",("No","Yes but not Physically Demanding","Yes and Physically demanding"))
    miss=st.checkbox("can the mother afford to miss a day of work for ANC or PHC visit")
    st.write("---")

    st.subheader("accessibility")
    distance_phc=st.number_input("Distance to nearest PHC or sub-centre in km(rough estimate is fine)",min_value=1,max_value=1000)
    transport=st.selectbox("Mode of transport available",("walking","two-wheeler","auto/taxi","none"))
    past_visit=st.checkbox("she has been to a government health facility before")
    submit=st.form_submit_button("submit details")
if submit==True:
    data={"name":name,
          "age":age,
          "state":state,
          "district":district,
          "ward":ward,
          "village":village,
          "phone":phone,
          "contact_no":contact_no,
          "caste":caste,
          "jsy":jsy,
          "jan_dhan":jan_dhan,
          "adahaar":adahaar,
          "no_preg":no_preg,
          "livebirth":livebirth,
          "miscarriage":miscarriage,
          "complications":complications,
          "delivery":delivery,
          "husband":husband,
          "prime_support":prime_support,
          "family_no":family_no,
          "female_support":female_support,
          "access_person":access_person,
          "prime_decider":prime_decider,
          "edu":edu,
          "read":read,
          "warn":warn,
          "pi_source":pi_source,
          "monthly_income":monthly_income,
          "does_she_work":does_she_work,
          "miss":miss,
          "distance_phc":distance_phc,
          "transport":transport,
          "past_visit":past_visit,
          "lmp":lmp
          }
    response=supabase.table("cases").insert(data).execute()
    st.success("data registered")
if st.button("Dashboard"):
    st.switch_page("pages/profiles_page.py")