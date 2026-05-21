import streamlit as st
medical_glossary="""
You are a maternal health risk assessment assistant supporting ANM (Auxiliary Nurse Midwife) workers in rural India.

You will receive a patient profile as a JSON dict. Here is what each field means:

--- IDENTITY & ANTHROPOMETRICS ---
id              : Unique patient ID
name            : Patient name
age             : Age in years
weight          : Weight in kg
height          : Height in cm
blood_group     : ABO + Rh blood group (e.g. "B+")
muac            : Mid-Upper Arm Circumference in cm (malnutrition indicator; <23cm = risk)
bmi             : Body Mass Index (null if height/weight missing)

--- PREGNANCY DATES ---
lmp             : Last Menstrual Period (date)
edd             : Expected Date of Delivery (date)
ga_weeks        : Gestational Age in complete weeks
ga_rem          : Remaining days beyond ga_weeks (e.g. ga=28w, ga_rem=3d)
trimester       : 1 / 2 / 3

--- OBSTETRIC HISTORY ---
gravida         : Total number of pregnancies including current
para            : Number of deliveries (live or stillbirth) after 20 weeks
abortions       : Number of pregnancy losses before 20 weeks
last_outcome    : Outcome of last pregnancy (e.g. "Normal", "C-Section", "Stillbirth") — null if primigravida
last_birth_weight : Birth weight of last baby in kg — null if primigravida
inter_pregnancy : Gap in months between last delivery and current LMP — null if primigravida
bad_obstetric   : Any prior bad obstetric history flag (e.g. PPH, eclampsia, neonatal death) — null if primigravida

--- CURRENT VITALS ---
bp_sys          : Systolic blood pressure in mmHg
bp_dia          : Diastolic blood pressure in mmHg
hb              : Hemoglobin in g/dL (normal ≥11 in pregnancy)
heart_rate      : Pulse in bpm
temp            : Body temperature in °F
blood_sugar     : Random blood sugar in mg/dL — null if not tested
urine_albumin   : Urine albumin result (e.g. "Nil", "Trace", "1+", "2+")
urine_sugar     : Urine sugar result (e.g. "Nil", "1+")

--- IMMUNIZATION & SUPPLEMENTS ---
tt_status       : Tetanus Toxoid status (e.g. "TT1 given", "TT2 given", "Not given")
tt_date         : Date TT was given — null if not given
ifa_given       : Iron-Folic Acid tablets given? (boolean)
calcium_given   : Calcium supplements given? (boolean)

--- MEDICAL CONDITIONS (all boolean) ---
diabetes        : Gestational or pre-existing diabetes
hypertension    : Pre-existing or pregnancy hypertension
thyroid         : Thyroid disorder
epilepsy        : Epilepsy / seizure disorder
hiv             : HIV positive status
sickle_cell     : Sickle cell disease or trait
other_condition : Any other condition noted (string or null)

--- FAMILY HISTORY (all boolean) ---
fam_twins       : Family history of twins
fam_diabetes    : Family history of diabetes
fam_hypertension: Family history of hypertension
fam_genetic     : Family history of genetic disorders

--- SOCIAL & ENVIRONMENTAL FACTORS ---
distance_phc    : Distance to Primary Health Centre in km
transport       : Access to transport (e.g. "Yes", "No", "Occasionally")
toilet          : Access to toilet at home (boolean or "Yes"/"No")
literacy        : Patient's literacy status (e.g. "Literate", "Illiterate")
husband_occupation : Husband's occupation (socioeconomic indicator)
meals_per_day   : Number of meals patient eats per day (nutritional indicator)

--- RISK ASSESSMENT & ANM NOTES ---
risk_level      : Computed risk level ("Low", "Medium", "High")
referral_needed : Whether referral to higher facility is needed ("No", "Yes - Urgent", "Yes - Routine")
referral_reason : Reason for referral — null if no referral
anm_notes       : Free-text notes entered by the ANM — null if none
supervisor_flag : Whether this case has been flagged for supervisor review (boolean)
"""
social_glossary="""
--- LOCATION ---
state           : State the patient resides in
district        : District within the state
ward            : Ward number or name (urban/peri-urban areas)
village         : Village name (rural areas)

--- CONTACT ---
phone           : Patient's own phone number
contact_no      : Alternate contact number (family member or neighbor)

--- IDENTITY & SCHEMES ---
caste           : Caste category (General / OBC / SC / ST) — affects scheme eligibility
jsy             : Enrolled in Janani Suraksha Yojana? (boolean) — cash incentive for institutional delivery
jan_dhan        : Has Jan Dhan bank account? (boolean) — required for DBT scheme payouts
adahaar         : Aadhaar number present/linked? (boolean) — required for govt scheme access

--- OBSTETRIC SUMMARY ---
no_preg         : Total number of pregnancies including current
livebirth       : Number of live births
miscarriage     : Number of miscarriages / spontaneous abortions
complications   : Any complications in previous pregnancies (string description or boolean)
delivery        : Mode/place of last delivery (e.g. "Home", "PHC", "Hospital", "C-Section")

--- HOUSEHOLD & SUPPORT SYSTEM ---
husband         : Husband's name
prime_support   : Primary support person during pregnancy (e.g. "Husband", "Mother-in-law")
family_no       : Total number of people in the household
female_support  : Is there a female family member available to support her? (boolean or name)
access_person   : Person who can be contacted or who accompanies her to health facility
prime_decider   : Who makes key decisions in the household (e.g. "Husband", "Mother-in-law", "Self")

--- EDUCATION & LITERACY ---
edu             : Highest education level (e.g. "Illiterate", "Primary", "Secondary", "Graduate")
read            : Can she read? (boolean) — determines if written materials are useful
warn            : Has she been counselled on warning signs of pregnancy? (boolean)
pi_source       : Primary source of pregnancy/health information (e.g. "ANM", "ASHA", "Family", "Phone")

--- ECONOMIC FACTORS ---
monthly_income  : Household monthly income in INR
does_she_work   : Is the patient currently employed / working? (boolean)
miss            : Will she miss work/income if she attends health visits? (boolean) — barrier to care

--- ACCESS TO CARE ---
distance_phc    : Distance to nearest Primary Health Centre in km
transport       : Access to transport for health visits (e.g. "Yes", "No", "Occasionally")
past_visit      : Number of ANC visits completed so far

--- PREGNANCY DATE ---
lmp             : Last Menstrual Period (date) — used to calculate gestational age
"""