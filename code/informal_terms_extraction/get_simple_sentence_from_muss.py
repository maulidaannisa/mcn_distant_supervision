from pymongo import MongoClient
import json
import os
from SPARQLWrapper import SPARQLWrapper, JSON
import spacy

import argparse

from muss.simplify import ALLOWED_MODEL_NAMES, simplify_sentences
from muss.utils.helpers import read_lines


client = MongoClient()

wiki_mongo = client.medical_wikipedia
wikimed = wiki_mongo.wikimed

def create_imput_file_for_muss():
	muss_data_source = [] 
	
	nlp = spacy.load('en_core_web_lg')

	for obj in wikimed.find():
		if 'sct' in obj.keys() and 'abstract' in obj.keys():
			doc = nlp(obj['abstract'])
			for sent in doc.sents:
				sentence = sent.text
				break
			item_sentence = {}
			item_sentence['item'] = obj['item']
			item_sentence['itemLabel'] = obj['itemLabel']
			item_sentence['sct'] = obj['sct']
			item_sentence['ori_sentence'] = sentence
			muss_data_source.append(item_sentence)
	print(muss_data_source)

	with open('muss_data_source_sct_update_2.json', 'w') as f:
		json.dump(muss_data_source, f)

	# with open('muss_source_sentences_sct.en', 'w') as f:
	# 	for item in muss_data_source:
	# 		f.write(item['ori_sentence'].strip('\n'))
	# 		f.write('\n')

def create_en_file():
	data = load_json('muss_data_source_sct_update_2.json')
	with open('muss_source_sentences_sct_update_2.en', 'w') as f:
		for d in data:
			f.write(d['ori_sentence'].strip('\n'))
			f.write('\n')

def load_json(json_file):
	with open(json_file, 'r') as f:
		json_data = json.load(f)

	return json_data

def load_en_file(en_file):
	with open (en_file, 'r') as f:
		en_data = f.readlines()

	return en_data

def write_json(data):
	with open('simple_sct_update_2.json','w') as json_file:
		json.dump(data, json_file)

def simplify(raw_muss_source_file, muss_data_source_file):
	raw_muss_source_data = load_json(raw_muss_source_file)
	muss_data_source = load_en_file(muss_data_source_file)


	print(len(raw_muss_source_data))
	print(len(muss_data_source))
	assert len(raw_muss_source_data) == len(muss_data_source)

	source_sentences = read_lines(muss_data_source_file)
	pred_sentences = simplify_sentences(source_sentences, model_name="muss_en_wikilarge_mined")
	
	simplify_results = []
	for c, s in zip(source_sentences, pred_sentences):
		simplify_results.append(s)
	write_json(simplify_results)
	
	with open ('item_with_ori_and_simple_sent_sct_update_2.json','w') as file:
		file.write('[')
		for idx, item in enumerate(raw_muss_source_data):
			item['simple_sent'] = simplify_results[idx]
			json.dump(item, file)
			file.write('\n')
		file.write(']')

# create_imput_file_for_muss()
# create_en_file()
raw_muss_source_data = 'muss_data_source_sct_update_2.json'
muss_data_source ='muss_source_sentences_sct_update_2.en'
simplify(raw_muss_source_data, muss_data_source)