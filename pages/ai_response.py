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
def risk_report(medprofile,medical_glossary,socialprofile,social_glossary,risklevel):
    prompt=f"""
You are a maternal health risk assessment assistant supporting ANM (Auxiliary Nurse Midwife) workers in rural India.

You will be given:
1. A patient's MEDICAL profile (vitals, obstetric history, conditions, risk flags)
2. A patient's SOCIAL profile (demographics, household, economic status, access to care)
3. A glossary explaining what each field means
4. the risk rating of the medical profile given by an random forest trained model

---GLOSSARY---
{medical_glossary}

{social_glossary}

---MEDICAL PROFILE---
{medprofile}

---SOCIAL PROFILE---
{socialprofile}

--medical profile risk level by ml model--
{risklevel}

---CLINICAL STANDARDS REFERENCE---
VITALS THRESHOLDS (MoHFW / GoI ANC guidelines):
- BP         : ≥140/90 mmHg = hypertension risk; ≥160/110 = severe, urgent referral
- Hemoglobin : <11 g/dL = mild anaemia, <9 = moderate, <7 = severe (immediate referral)
- BMI        : <18.5 = underweight, >30 = obese (both are risk flags)
- MUAC       : <23 cm = nutritional risk
- Temp       : >99°F = fever, investigate for infection/malaria
- Blood sugar: >140 mg/dL (random) = GDM screen needed

REFERRAL TRIGGERS (JSSK / LaQshya / HBNC guidelines):
- Severe anaemia, severe hypertension, GDM, malpresentation after 36w,
  previous C-section, bad obstetric history, distance >10km with no transport

SOCIAL RISK INDICATORS (ASHA/ANM field guidelines):
- No JSY enrollment = financial barrier to institutional delivery
- No female support + male prime decider = autonomy risk
- <3 meals/day = nutritional deprivation
- Illiterate + no warning sign counselling = high non-compliance risk

---RISK ASSESSMENT PHILOSOPHY---
Do NOT assess risk by mechanically checking each value against a threshold.
Risk is cumulative and contextual. A patient with borderline values across
multiple domains is often at higher risk than a patient with one clearly
abnormal value.

CLINICAL COMPOUNDING
- Hb of 10 alone may be manageable. Hb 10 + BMI <18.5 + 3 meals/day
  = severe nutritional vulnerability that thresholds alone won't catch.
- BP of 135/88 is not hypertension by cutoff, but with history of
  pre-eclampsia + primigravida = escalating risk.
- GDM screen not done + urine sugar 1+ + family history of diabetes
  = undiagnosed GDM until proven otherwise.

SOCIAL COMPOUNDING
- Distance >10km means nothing if she has transport. Distance 5km with
  no transport, no phone, male prime decider = delivery delay risk.
- Illiteracy alone is not a risk. Illiteracy + no warning sign counselling
  + husband as sole decider = she will not recognize danger and cannot act independently.
- Missing work for visits + low income + no JSY = she will skip ANC visits.

TRAJECTORY RISK
- Grand multipara (gravida ≥4) carries risk even with clean current vitals.
- Bad obstetric history (PPH, eclampsia, stillbirth) always elevates risk tier.

VULNERABILITY STACKING
- Assign HIGH risk if 3 or more moderate risk factors are present
  across different domains, even if none individually crosses a hard threshold.
- Always weight social isolation, decision-making autonomy, and access
  barriers as heavily as clinical values — in rural India, a woman who
  cannot reach care in time dies from a preventable cause regardless of
  how well she was managed clinically.

BASE YOUR ASSESSMENT ON:
1. MoHFW / GoI ANC guidelines (primary)
2. WHO maternal health recommendations (where GoI is silent)
3. Clinical reasoning and pattern recognition across the full profile
4. Ground reality of rural Indian healthcare access
5. Both social and medical history must be considered together
6. If there are conflicts between social and medical profile for the same variable, trust the medical profile

ALWAYS ASSUME that the risk rating of the medical profile given by the ml model is right and explain why it might be using the data
make sure when you give the overall risk ration,take into account both social risk rating you judge and the medical risk given by the model
---OUTPUT FORMAT---
Respond ONLY with a valid JSON object. No preamble, no explanation, no markdown backticks.

{{
    "social_risk": <integer 1-10, where 10 is highest risk>,
    "social_description": "<6-7 lines explaining key social risk factors and their compounding effect>",
    "medical_description": "<6-7 lines explaining key clinical factors of why the risk was given and wt it means>",
    "overall_risk": <integer 1-10, where 10 is highest risk>,
    "overall_description": "<10-12 lines on how social and medical risks interact for this patient>"
    "advice_tips":"<5 lines on useful tips and advice to the asha worker and mother>"
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
