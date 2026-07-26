import google.generativeai as genai
import streamlit as st
from supabase import create_client
import json
from pages.golssary import medical_glossary 
from pages.golssary import social_glossary
supabase=create_client(st.secrets["SUPABASE_URL"],st.secrets["SUPABASE_KEY"])
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model=genai.GenerativeModel("gemini-flash-latest")
id=st.session_state["profileid"]
medprofile=supabase.table("medical_cases").select("*").eq("id",id).execute().data[0]
socialprofile=supabase.table("cases").select("*").eq("id",id).execute().data[0]


#prompt part start
def query_answer(medprofile,medical_glossary,socialprofile,social_glossary,query):
    prompt=f"""
you are a supportive AI assistant embedded in a healthcare and social-context application, used by mothers mostly rural for their medical, pregnancy,
childcare or social circumstances questions

You will be given:
1. A patient's MEDICAL profile (vitals, obstetric history, conditions, risk flags)
2. A patient's SOCIAL profile (demographics, household, economic status, access to care)
3. A glossary explaining what each field means
4. the question or query asked by the mother

---GLOSSARY---
{medical_glossary}

{social_glossary}

---MEDICAL PROFILE---
{medprofile}

---SOCIAL PROFILE---
{socialprofile}

---query or question to be asked---
{query}
 read the query given and use the data above as reference and understand the case well and use the context of the case and its medical and social risk porfile and answer the query as supportively as possible using external info and the info from the user profile as well

---OUTPUT FORMAT---
Respond ONLY with a valid JSON object. No preamble, no explanation, no markdown backticks.

{{
    "answer": <6-7 lines answering their query but reasonably you can use 10 lines but not more than that. make the answer accurate to the question>
}}
"""
    response=model.generate_content(prompt)
    return parse_json_response(response.text)
   
def parse_json_response(text):
    try:
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {str(e)}", "raw": text}
#prompt part end