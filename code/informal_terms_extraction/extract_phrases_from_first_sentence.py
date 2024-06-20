import spacy
from medcat.vocab import Vocab
from medcat.cat import CAT
from medcat.cdb import CDB
from sentence_similarity import SentenceSimilarity
import json
from tqdm import tqdm
from scispacy.abbreviation import AbbreviationDetector

models = ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "multi-qa-mpnet-base-dot-v1", "nq-distilbert-base-v1", "allenai-specter" ]#, "all-distilroberta-v1"]


nlp = spacy.load("en_core_web_md")
nlp_sci = spacy.load("en_core_sci_sm")
nlp_sci.add_pipe("abbreviation_detector")

# load medcat
# vocab_path = 'models/vocab.dat'
cdb_path = 'models/SNOMED_cdb.dat'

# Load the vocab model you downloaded
# vocab = Vocab.load(vocab_path)
# Load the cdb model you downloaded
cdb = CDB.load(cdb_path)

def get_noun_phrases(text):
    doc = nlp(text)
    nps = []

    for token in doc.noun_chunks:
        nps.append(token)
    
    return nps

def get_abbreviation(text):
    doc = nlp_sci(text)

    abbr = []
    for abrv in doc._.abbreviations:
        abbr.append(str(abrv))
        # print(f"{abrv} \t ({abrv.start}, {abrv.end}) {abrv._.long_form}")

    return abbr


def get_extended_noun_phrases(text):
    doc = nlp(text)

    index = 0
    nounIndices = []
    for token in doc:
        if token.pos_ == 'NOUN':
            nounIndices.append(index)
        index = index + 1  
        
    spans = []
    for i in nounIndices:
        span = doc[doc[i].left_edge.i : doc[i].right_edge.i+1]
        if span.text not in ' '.join(map(lambda e: e.text, spans)):
            spans.append(span)

    str_spans = [str(span) for span in spans]

    return str_spans

def get_inlink_re_mapping():
    f = open("wikimed.json", encoding='utf-8')
    data = json.load(f)
    sct_map = {}

    for i in data:
        if "sct" in i:
            re_set = set()
            inlink_set = set()
            if "rn" in i:
                re_set = set(i["rn"])
            
            if "inlink" in i:
                inlink_set = set(i["inlink"])

            final_set = re_set.union(inlink_set)

            for phrase in final_set:
                if i["sct"] not in sct_map:
                    sct_map[i["sct"]] = [phrase]
                else:
                    sct_map[i["sct"]].append(phrase)

    return sct_map

def get_snomed_from_cui(sct_code):
    prefered_name = cdb.get_name(sct_code)

    return prefered_name

def remove_if_exists(L, value):
  try:
    L.remove(value)
  except ValueError:
    pass

  return L


def run_model(MODEL_NAME):

    # MODEL_NAME = "all-distilroberta-v1"
    THRESHOLD = 0.8

    PRE_FILE_NAME = "raw_data_comparison-{}".format(MODEL_NAME)
    PRE_FILE_PATH = "result-mcn-first-sentence/{}.json".format(PRE_FILE_NAME)

    FILE_OUTPUT_NAME = "mcn_distant-{}-{}".format(MODEL_NAME, str(abs(THRESHOLD*100)))
    FILE_OUTPUT_PATH = "result-mcn-first-sentence/{}.txt".format(FILE_OUTPUT_NAME)

    sim = SentenceSimilarity(model_name=MODEL_NAME, threshold=THRESHOLD)
    # sim = SentenceSimilarity(pre_file_name=PRE_FILE_PATH)

    simple_file = "item_with_ori_and_simple_sent_sct_update_2.json"

    inlink_re_map = get_inlink_re_mapping()

    f = open(simple_file, encoding='utf-8')
    data = json.load(f)

    mcn_data = []
    raw_data_comparison = {}

    for d in tqdm(data):
        # 1st ground truth from wiki itemlabel
        ground_truth = [d["itemLabel"]]
        
        # 2nd ground truth from Snomed Title
        concept_name = get_snomed_from_cui(d['sct'])
        if concept_name != d['sct']:
            # concept not found in MedCat CDB
            ground_truth.append(concept_name)

        # 3rd ground truth from inlink and re
        if d["sct"] in inlink_re_map:
            ground_truth.extend(inlink_re_map[d["sct"]])

        # remove duplicate
        ground_truth = list(set(ground_truth))

        # get extended noun phrases from first sentence, and simple first sentence
        ext_noun_phrases = []
        ext_noun_phrases.extend(get_extended_noun_phrases(d["ori_sentence"]))
        ext_noun_phrases.extend(get_extended_noun_phrases(d["simple_sent"]))

        # remove duplicate
        ext_noun_phrases = list(set(ext_noun_phrases))

        # remove, if it already exists in ground truth
        for phrase in ground_truth:
            ext_noun_phrases = remove_if_exists(ext_noun_phrases, phrase)

        # remove with custom stopwords
        med_stopwords = ['a disease', 'disease', 'It', 'it', 'a medical condition']
        for phrase in med_stopwords:
            ext_noun_phrases = remove_if_exists(ext_noun_phrases, phrase)

        # it might end up in empty noun phrases
        if len(ext_noun_phrases) == 0:
            continue

        new_phrases = []

        if sim.mode == 'model':
            new_phrases, cosine_scores = sim.get_semantically_similar_phrases(ground_truth, ext_noun_phrases)

            for i in range(len(ground_truth)):
                for j in range(len(ext_noun_phrases)):
                    raw_data_comparison[ground_truth[i] + " ## " + ext_noun_phrases[j]] = str(cosine_scores[i][j])
        else:
            new_phrases = sim.get_semantically_similar_phrases_pre(ground_truth, ext_noun_phrases)

        # get abbreviations
        new_phrases.extend(get_abbreviation(d["ori_sentence"]))
        new_phrases.extend(get_abbreviation(d["simple_sent"]))

        new_phrases = list(set(new_phrases))

        for phrase in new_phrases:
            mcn_data.append("__label__{} {}".format(d["sct"], phrase))


    with open(FILE_OUTPUT_PATH, 'w', encoding='utf-8') as f:
      for line in mcn_data:
        f.write(line + "\n")

    if sim.mode == 'model':
        with open(PRE_FILE_PATH, "w") as outfile:
            json.dump(raw_data_comparison, outfile)

for model in models:
    print(model)
    run_model(model)