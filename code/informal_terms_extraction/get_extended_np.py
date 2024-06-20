import spacy

nlp = spacy.load("en_core_web_md")

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


text = "Vitamin K deficiency bleeding (VKDB) of the newborn, previously known as haemorrhagic disease of the newborn, is a condition in which the baby does not get enough vitamin K at birth."

print(get_extended_noun_phrases(text))