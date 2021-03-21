

In [119]: from logic import check_similarity


In [119]: import json
     ...: import nltk
     ...: import functools
     ...: from collections import Counter
     ...: from nltk.stem import WordNetLemmatizer
     ...: from sklearn.linear_model import LogisticRegression
     ...: from sklearn.feature_extraction import DictVectorizer
     ...: from sklearn.model_selection import train_test_split, cross_validate
     ...: from sklearn.metrics import classification_report
     ...: from text_preprocessing import prepare_text

     ...: from database_functions import (
     ...:     get_body,
     ...:     get_symptom,
     ...:     get_hackathon_order,
     ...:     get_doctor_specs,
     ...:     get_specs
     ...: )
     ...: 
     ...: orders = get_hackathon_order()
     ...: 
     ...: data = []
     ...: for i,(doctor_id,specialty_id,comment,adult,gender) in enumerate(orders):
     ...:     print(i)
     ...:     doctor_specs = get_doctor_specs(doctor_id)
     ...:     specs = get_specs(doctor_specs) if not specialty_id else get_specs(((specialty_id,),))
     ...:     if not specs or not comment:
     ...:         continue
     ...:     data.append([specs[0][0], comment,adult,gender])
     ...: 
     ...: symptoms = get_symptom()

In [119]: import langdetect
     ...: import re


In [119]: log_res = LogisticRegression(random_state=42, multi_class='multinomial',
     ...:                          solver='sag', max_iter=300)


In [119]: dict_vec = DictVectorizer()


In [119]: info = []
     ...: prepared_symptoms = [(symptom[0], symptom[1], symptom[2], prepare_text(symptom[2])) for symptom in symptoms]
     ...: for i,(label, comment,adult,gender) in enumerate(data):
     ...:     print(i)
     ...:     order_detected_symptoms = []
     ...:     if not comment or re.search(r'[ЁёА-я]',comment) is None or langdetect.detect(comment) != 'ru':
     ...:         continue
     ...:     comment_tokens = prepare_text(comment)
     ...:     comment_tokens = [f'{t[0]}_{t[1]}' for t in comment_tokens]
     ...:     similarities = []
     ...:     for j,(sym_id,body_id,symptom,symptom_tokens) in enumerate(prepared_symptoms):
     ...:         symptom_tokens = [f'{t[0]}_{t[1]}' for t in symptom_tokens]
     ...:         if not comment_tokens or not symptom_tokens:
     ...:             continue
     ...:         try:
     ...:             similarity = check_similarity(comment_tokens,symptom_tokens)
     ...:         except ZeroDivisionError:
     ...:             continue
     ...:         if similarity > 0.80:
     ...:             similarities.append((sym_id,symptom,similarity))
     ...:     if similarities:
     ...:         max_similar_symptom= max(similarities, key=lambda x: x[2])
     ...:         print("!!!!!!!",doctor_id,label,max_similar_symptom, comment_tokens[:10])
     ...:         ss = [str(s[0]) for s in similarities]
     ...:         #for s in ss:
     ...:         #    order_detected_symptoms.append({'symptom':s,'gender':gender,'adult':adult})
     ...:         #if order_detected_symptoms:
     ...:         info.append([label, {'symptoms':ss,'gender':gender,'adult':adult}])
     ...: 


In [119]: for item in info:
     ...:     if item[1]['gender'] == 'male':
     ...:         item[1]['gender'] = 1
     ...:     elif item[1]['gender'] == 'female':
     ...:         item[1]['gender'] = 2
     ...:     else:
     ...:         item[1]['gender'] = 0

In [119]: import random

In [119]: random.shuffle(info)


In [119]: prepared_dataset = info


In [119]: train_dataset, test_dataset = prepared_dataset[:round(0.8*len(prepared_dataset))], prepared_dataset[round(0.8*len(prepared_dataset)):]


In [119]: X_train_tokens = [item[1] for item in train_dataset]
     ...: y_train_labels = [item[0] for item in train_dataset]
     ...: 
     ...: X_test_tokens = [item[1] for item in test_dataset]
     ...: y_test_labels = [item[0] for item in test_dataset]


In [119]: vectorized_features = dict_vec.fit_transform(X_train_tokens)


In [119]: log_res.fit(vectorized_features, y_train_labels)


In [119]: print(classification_report(y_test_labels, log_res.predict(dict_vec.transform(X_test_tokens))))


In [119]: import pickle
     ...: with open('log_res_model.pickle','w') as f:
     ...:     pickle.dump(log_res,f)
