import joblib
import numpy as np
import pandas as pd

model = joblib.load('pages/asha_risk_model.pkl')

def predict_risk(data):
    # ordinal encoding
    albumin_map = {'Nil':0,'Trace':1,'1+':2,'2+':3,'3+':4}
    sugar_map = {'Nil':0,'1+':1,'2+':2}
    tt_map = {'Not given':0,'TT1 given':1,'TT2 given':2,'Booster given':2,'Previously protected':2}
    outcome_map = {'None':0,'Normal':1,'C-Section':2,'Stillbirth':3,'Abortion':4}
    label_map = {0:'Low',1:'Medium',2:'High'}

    trimester_map = {
    "1st Trimester": 1,
    "2nd Trimester": 2,
    "3rd Trimester": 3,
    "1": 1,
    "2": 2,
    "3": 3,
    1: 1,
    2: 2,
    3: 3
}
    row = {
        'age': data['age'],
        'weight': data['weight'],
        'height': data['height'],
        'muac': data['muac'],
        'bmi': data['bmi'],
        'ga_weeks': data['ga_weeks'],
        'ga_rem': data['ga_rem'],
        'trimester': trimester_map[data['trimester']],
        'gravida': data['gravida'],
        'para': data['para'],
        'abortions': data['abortions'],
        'last_birth_weight': data['last_birth_weight'] if data['last_birth_weight'] else 0,
        'inter_pregnancy': data['inter_pregnancy'] if data['inter_pregnancy'] else 0,
        'bad_obstetric': int(data['bad_obstetric']) if data['bad_obstetric'] else 0,
        'bp_sys': data['bp_sys'],
        'bp_dia': data['bp_dia'],
        'hb': data['hb'],
        'heart_rate': data['heart_rate'],
        'temp': data['temp'],
        'blood_sugar': data['blood_sugar'] if data['blood_sugar'] else 95,
        'urine_albumin': albumin_map[data['urine_albumin']],
        'urine_sugar': sugar_map[data['urine_sugar']],
        'tt_status': tt_map[data['tt_status']],
        'ifa_given': int(data['ifa_given']),
        'calcium_given': int(data['calcium_given']),
        'diabetes': int(data['diabetes']),
        'hypertension': int(data['hypertension']),
        'thyroid': int(data['thyroid']),
        'epilepsy': int(data['epilepsy']),
        'hiv': int(data['hiv']),
        'sickle_cell': int(data['sickle_cell']),
        'fam_twins': int(data['fam_twins']),
        'fam_diabetes': int(data['fam_diabetes']),
        'fam_hypertension': int(data['fam_hypertension']),
        'fam_genetic': int(data['fam_genetic']),
        # one-hot blood group
        'blood_group_A+': int(data['blood_group']=='A+'),
        'blood_group_A-': int(data['blood_group']=='A-'),
        'blood_group_AB+': int(data['blood_group']=='AB+'),
        'blood_group_AB-': int(data['blood_group']=='AB-'),
        'blood_group_B+': int(data['blood_group']=='B+'),
        'blood_group_B-': int(data['blood_group']=='B-'),
        'blood_group_O+': int(data['blood_group']=='O+'),
        'blood_group_O-': int(data['blood_group']=='O-'),
        # one-hot last outcome
        'last_outcome_C-Section': int(data['last_outcome']=='C-Section'),
        'last_outcome_None': int(data['last_outcome'] is None),
        'last_outcome_Normal': int(data['last_outcome']=='Normal'),
        'last_outcome_Stillbirth': int(data['last_outcome']=='Stillbirth'),
    }

    df_input = pd.DataFrame([row])
    prediction = model.predict(df_input)[0]
    return label_map[prediction],row
