import sqlite3

def get_body():
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute('SELECT id,name FROM body')
    result = cur.fetchall()
    con.close()

    return result

def get_body_symptom_disease_id(body_symptom_id):
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute('SELECT disease_id FROM disease_body_symptom where body_symptom_id=?', (body_symptom_id,))
    result = cur.fetchall()
    con.close()

    return result

def get_symptom_disease_id(symptom_id):
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute('SELECT disease_id FROM disease_symptom where symptom_id=?', (symptom_id,))
    result = cur.fetchall()
    con.close()

    return result

def get_body_symptom_id(body_id, symptom_id):
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute('SELECT id FROM body_symptom where symptom_id=? and body_id=?', (symptom_id,body_id))
    result = cur.fetchall()
    con.close()

    return result

def get_disease(disease_id):
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute('SELECT name FROM disease where id=?', (disease_id,))
    result = cur.fetchone()
    con.close()

    return result

def get_symptom():
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute('SELECT id,body_id,name FROM symptom')
    result = cur.fetchall()
    con.close()

    return result

def get_hackathon_order():
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute("SELECT doctor_id,specialty_id,comment,adult,gender FROM hackathon_order where mainStatus='complete'")
    result = cur.fetchall()
    con.close()

    return result

def get_doctor_specs(doctor_id):
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute('SELECT specialty_id FROM doc_spec where doctor_id=?', (doctor_id,))
    result = cur.fetchall()
    con.close()

    return result

def get_spec_docs(spec_id):
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute('SELECT doctor_id FROM doc_spec where specialty_id=?', (spec_id,))
    result = cur.fetchall()
    con.close()

    return result

def get_doc_diseases(doc_id):
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute('SELECT dis_id FROM doctor_diseases where doc_id=?', (doc_id,))
    result = cur.fetchall()
    con.close()

    return result

def get_specs(spec_ids):
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    placeholder = '?' * len(spec_ids)
    cur.execute(f'SELECT name FROM specialty where id in ({",".join(placeholder)})', tuple(s[0] for s in spec_ids))
    result = cur.fetchall()
    con.close()

    return result

def get_spec_id(spec_name):
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute(f'SELECT id FROM specialty where name=?',(spec_name,))
    result = cur.fetchone()
    con.close()

    return result

def get_user(telegram_id):
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM user where telegram_id=?',(telegram_id,))
    result = cur.fetchone()
    con.close()

    return result

def add_user(telegram_id, adult, gender):
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute(f'INSERT INTO user (telegram_id, adult, gender) VALUES (?,?,?)',(telegram_id,adult,gender,))
    con.commit()
    con.close()

def update_user(telegram_id, adult, gender):
    con = sqlite3.connect('health_bot.db')
    cur = con.cursor()
    cur.execute(f'UPDATE user SET adult=?, gender=? where telegram_id=?',(adult,gender,telegram_id,))
    con.commit()
    con.close()