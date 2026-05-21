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
You are a supportive healthcare assistant for rural maternal health cases.

You are given:
- Medical profile
- Social profile
- Glossary
- User query

Your job:
1. First understand the case using medical + social context
2. Then directly answer the user's query clearly and practically
3. Keep language simple and supportive

---MEDICAL PROFILE---
{medprofile}

---SOCIAL PROFILE---
{socialprofile}

---QUERY---
{query}

---OUTPUT FORMAT---
Return ONLY valid JSON:

{{
  "answer": "First 3-4 lines: brief case understanding. Next 6-10 lines: direct answer to the user's query in practical, actionable language."
}}

Rules:
- ALWAYS answer the query explicitly
- Do NOT stop at case summary
- Do NOT ignore the question
- No markdown, no extra text outside JSON
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
