import sqlite3
import pymorphy2
import gensim.downloader as api
import gensim
import nltk
import pickle
import re
import langdetect
import json
from collections import defaultdict

from database_functions import (
    get_symptom, 
    get_body, 
    get_disease, 
    get_symptom_disease_id, 
    get_body_symptom_disease_id,
    get_body_symptom_id,
    get_spec_docs,
    get_doc_diseases,
    get_spec_id
)
from text_preprocessing import prepare_text
from sklearn.feature_extraction import DictVectorizer


model = gensim.models.KeyedVectors.load_word2vec_format('../models/news_upos_skipgram_300_5_2019/model.bin', binary=True)
VOCAB = model.vocab



def check_similarity(input_tokens,db_tokens):
    filtered_input_tokens = []
    for token in input_tokens:
        if token in VOCAB:
            filtered_input_tokens.append(token)
    filtered_db_tokens = []
    for token in db_tokens:
        if token in VOCAB:
            filtered_db_tokens.append(token)

    return model.n_similarity(filtered_input_tokens,filtered_db_tokens)

def get_answer(comment,adult,gender):
    print(comment)
    info = []
    symptoms = get_symptom()
    prepared_symptoms = [(symptom[0], symptom[1], symptom[2], prepare_text(symptom[2])) for symptom in symptoms]
    if not comment or re.search(r'[ЁёА-я]',comment) is None or langdetect.detect(comment) != 'ru':
        return "Не достаточно симптомов"
    comment_tokens = prepare_text(comment)
    print(comment_tokens)
    comment_tokens = [f'{t[0]}_{t[1]}' for t in comment_tokens]
    body_parts = get_body_parts(comment_tokens)
    similarities = []
    print(comment_tokens)
    for j,(sym_id,body_id,symptom,symptom_tokens) in enumerate(prepared_symptoms):
        symptom_tokens = [f'{t[0]}_{t[1]}' for t in symptom_tokens]
        if not comment_tokens or not symptom_tokens:
            continue
        try:
            similarity = check_similarity(comment_tokens,symptom_tokens)
        except ZeroDivisionError:
            continue
        if similarity > 0.80:
            similarities.append((sym_id,symptom,similarity, body_id))
    if similarities:
        max_similar_symptom= max(similarities, key=lambda x: x[2])
        ss = [str(s[0]) for s in similarities]
        analysis = defaultdict(list)
        all_diseases = dict()
        all_diseases_ids = []
        info.append({'symptoms':ss,'gender':gender,'adult':adult})
        for sym_id,symptom,similarity, body_id in similarities:
            if body_parts:
                for body_id,_ in body_parts:
                    diseases,diseases_ids = get_disease_by_body_symptoms(body_id,sym_id)
                    all_diseases.update(diseases)
                    all_diseases_ids.extend(diseases_ids)
            elif body_id:
                diseases,diseases_ids = get_disease_by_body_symptoms(body_id,sym_id)
                all_diseases.update(diseases)
                all_diseases_ids.extend(diseases_ids)
            else:
                diseases,diseases_ids = get_disease_by_symptom([sym_id,])
                all_diseases.update(diseases)
                all_diseases_ids.extend(diseases_ids)
                
    if info:
        answer = []
        with open('log_res_model.pickle','rb') as f:
            model = pickle.load(f)
        with open('dict_vec.pickle','rb') as f:
            dict_vec = pickle.load(f)
        doctor = model.predict(dict_vec.transform(info))
        if doctor:
            
            answer.append(f"**Рекомендуемый специалист**: _{doctor[0]}_\n")
            all_diseases_ids = list(set(all_diseases_ids))
            spec_id = get_spec_id(doctor[0])
            docs = get_spec_docs(spec_id[0])
            for id in all_diseases_ids:
                found = False
                for doc_id in docs:
                    # print(doc_id)
                    doc_dis = [d[0] for d in get_doc_diseases(doc_id[0])]
                    if id in doc_dis:
                        found = True
                if not found:
                    all_diseases_ids.remove(id)
            for id in all_diseases_ids:
                analysis[all_diseases[id]].extend(get_analysis(id))
            if analysis:
                answer.append("**Возможные диагнозы и обследования**: \n")
                for disease, analysis_list in analysis.items():
                    answer.append(f"_Диагноз_: {disease}\n")
                    answer.append(f"_Обследования_: {';'.join(analysis_list)}\n")

        
        return " ".join(answer)
    
    return "Не достаточно симптомов"

def get_body_parts(comment_tokens):
    similarities = []
    body_parts = get_body()
    prepared_body_parts = [(body_part[0], prepare_text(body_part[1])) for body_part in body_parts]
    for body_id, part_tokens in prepared_body_parts:
        part_tokens = [f'{t[0]}_{t[1]}' for t in part_tokens]
        if not comment_tokens or not part_tokens:
            continue
        try:
            similarity = check_similarity(comment_tokens,part_tokens)
        except ZeroDivisionError:
            continue
        if similarity > 0.80:
            similarities.append((body_id,similarity))

    return similarities

def get_disease_by_symptom(symptom_ids):
    all_diseases_ids = set()
    for symptom_id in symptom_ids:
        disease = get_symptom_disease_id(symptom_id)
        for disease in diseases:
            all_diseases_ids.add(disease[0])
    all_diseases = dict()
    for disease_id in all_diseases_ids:
        all_diseases[disease_id] = get_disease(disease_id)[0]
    print(all_diseases, all_diseases_ids)
    return all_diseases, all_diseases_ids



def get_disease_by_body_symptoms(body_id, symptom_id):
    all_diseases_ids = set()
    body_symptoms = get_body_symptom_id(body_id, symptom_id)
    for body_symptom in body_symptoms:
        diseases = get_body_symptom_disease_id(body_symptom[0])
        for disease in diseases:
            all_diseases_ids.add(disease[0])
    all_diseases = dict()
    for disease_id in all_diseases_ids:
        all_diseases[disease_id] = get_disease(disease_id)[0]
    print(all_diseases, all_diseases_ids)
    return all_diseases, all_diseases_ids

def get_analysis(disease_id):
    with open('analysis.json','r') as f:
        analysis = json.load(f)
    
    return analysis.get(str(disease_id),[])