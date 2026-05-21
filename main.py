from supabase import create_client
import streamlit as st
st.set_page_config(layout="wide")

st.title("ASHA.AI")
st.subheader("Simplifying healthcare workflows at the grassroots level.")

@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
supabase = init_supabase()
def register(email,password,name,role):
    res=supabase.auth.sign_up({
        "email":email,
        "password":password
    })
    if res.user:
        supabase.table("profiles").insert({
            "id":res.user.id,
            "name":name,
            "role":role
        }).execute()
        return "Account created successfully"
    return "registration failed"

def login(email,password):
    res=supabase.auth.sign_in_with_password({
        "email":email,
        "password":password
    })
    if res.user:
        st.session_state.user=res.user
        st.session_state.session=res.session
        return "Logged in successfully"
    return "Log in unsuccessful"

def isloggedin():
    return "user" in st.session_state and st.session_state.user is not None
tab1,tab2=st.tabs(["login","register"])

@st.dialog("login", width="small", dismissible=True, on_dismiss="ignore")
def log_in():
    email=st.text_input("email")
    password=st.text_input("Password")

with tab2:
    name=st.text_input("name")
    email=st.text_input("email")
    password=st.text_input("Password",type="password")
    role=st.selectbox("Signing up as:",["Accredited Social Health Activist (ASHA)","Auxiliary Nurse Midwife (ANM)","Supervisor"])
    if st.button("Register"):
        message = register(email, password, name, role)
        st.write(message)
with tab1:
    email=st.text_input("email",key="email")
    password=st.text_input("Password",key="password",type="password")
    if st.button("log in"):
        message = login(email,password)
        st.write(message)

if not isloggedin():
    isloggedin()
else:
    st.switch_page("pages/profiles_page.py")
