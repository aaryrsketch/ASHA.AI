import streamlit as st
from supabase import create_client
st.set_page_config(layout="wide")
#the role code
@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
supabase = init_supabase()
user=st.session_state.user
res=supabase.table("profiles").select("name,role").eq("id",user.id).single().execute()
if res.data:
    st.session_state.profile=res.data
#ends heree
response = supabase.table("cases").select("*",count="exact").execute()
case_no=response.count
l1=[]
if res.data["role"]=="Accredited Social Health Activist (ASHA)":
    st.title("ASHA Dashboard")
    st.markdown("Here you can add new profiles or update or look up existing profiles ")   
    st.metric("TOTAL CASES", f"{case_no}","one new case this week !!")
    st.write("---")
    if st.button("Add profile"):
        st.switch_page("pages/New_Profile.py")
    
elif res.data["role"]=="Auxiliary Nurse Midwife (ANM)":
    st.title("ANM Dashboard")
    st.metric("number of cases recorded and live", f"{case_no}","one new case added this week")
    st.write("---")


cases=supabase.table("cases").select("*").order("id").execute().data
for i, row in enumerate(cases):
    with st.expander(f"Case {i+1}: {row['name']}"):
        st.write("Name:", row["name"])
        st.write(f"Age: {row["age"]}")
        st.write("State:", row["state"])
        st.write(f"Contact number: { row["contact_no"]}")
        if st.button("Profile details",key=f"profile{i}"):
            st.session_state["profileid"]=row["id"]
            st.switch_page("pages/profile.py")
        if st.button("Medical Data",key=f"medic profile{i}"):
            st.session_state["profileid"]=row["id"]
            st.switch_page("pages/medical_profile.py")