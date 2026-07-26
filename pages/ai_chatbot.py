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
<<<<<<< HEAD
you are a supportive AI assistant embedded in a healthcare and social-context application, used by mothers mostly rural for their medical, pregnancy,
childcare or social circumstances questions
=======
You are a supportive healthcare assistant for rural maternal health cases.
>>>>>>> 1627cdeb9c901edd32afe38b1f88ab7106a75623

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
<<<<<<< HEAD
 read the query given and use the data above as reference and understand the case well and use the context of the case and its medical and social risk porfile and answer the query as supportively as possible using external info and the info from the user profile as well
=======
>>>>>>> 1627cdeb9c901edd32afe38b1f88ab7106a75623

---OUTPUT FORMAT---
Return ONLY valid JSON:

{{
<<<<<<< HEAD
    "answer": <6-7 lines answering their query but reasonably you can use 10 lines but not more than that. make the answer accurate to the question>
=======
  "answer": "First 3-4 lines: brief case understanding. Next 6-10 lines: direct answer to the user's query in practical, actionable language."
>>>>>>> 1627cdeb9c901edd32afe38b1f88ab7106a75623
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
