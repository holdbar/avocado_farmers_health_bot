import nltk
import pymorphy2
import string

nltk.download('stopwords')
from nltk.corpus import stopwords
STOP_WORDS = stopwords.words("russian") + [p for p in string.punctuation]
morph = pymorphy2.MorphAnalyzer()

tag_mapping = {"ADJF": "ADJ", "ADJS": "ADJ", "COMP": "ADJ", "PRTF": "ADJ",
           "PRTS": "ADJ", "GRND": "VERB", "NUMR": "NUM", "ADVB": "ADV",
           "NPRO": "PRON", "PRED": "ADV", "PREP": "ADP", "PRCL": "PART"}

def prepare_text(text):
    tokens = nltk.word_tokenize(text,language='russian')
    tokens = [t.lower().strip("\\") for t in tokens if t.lower() not in STOP_WORDS]
    parsed_tokens = [morph.parse(t)[0] for t in tokens]
    prepared_tokens = []
    for pt in parsed_tokens:
        lemma = 'стопа' if pt.normal_form == 'стоп' else pt.normal_form
        tag = tag_mapping[pt.tag.POS] if pt.tag.POS in tag_mapping else pt.tag.POS
        prepared_tokens.append((lemma, tag))
    
    return prepared_tokens

