from pymongo import MongoClient
import json
import os
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import wikipedia
from urllib.parse import unquote
import spacy
import argparse

from muss.simplify import ALLOWED_MODEL_NAMES, simplify_sentences
from muss.utils.helpers import read_lines


client = MongoClient()

wikiredirects_db= client.wiki_redirect
redirects = wikiredirects_db.redirects

wiki_inlinks = client.wiki_inlink
wikilink = wiki_inlinks.inlinks

wikisct_db = client.wiki_snomed
wikimed = wikisct_db.wikimed


def get_redirect(itemLabel):
	redirect_list = []

	for rd in redirects.find({'title':itemLabel}):
			redirect_list.append(rd['redirect_link'])

	if len(redirect_list) != 0:
		return redirect_list

	else:
		for rn in redirects.find({"redirect_link":itemLabel}):
			if len(rn) !=0:
				wiki=rn['title']
				for t in redirects.find({"title":wiki}):
					redirect_list.append(t['redirect_link'])
				
		return redirect_list

def get_wikilinks(itemLabel):
	wikilink_list = []

	for wl in wikilink.find({'title':itemLabel}):
			wikilink_list.append(wl['inlink'])

	if len(wikilink_list) != 0:
		return wikilink_list

	else:
		for il in wikilink.find({"inlink":itemLabel}):
			if len(il) !=0:
				wiki=il['title']
				for t in wikilink.find({"title":wiki}):
					wikilink_list.append(t['inlink'])
			return wikilink_list

def abstract_query(param):
	sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	query = """
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	PREFIX dbo: <http://dbpedia.org/ontology/>
	SELECT DISTINCT ?name ?abstract WHERE { 
	  [ rdfs:label ?name
	  ; dbo:abstract ?abstract
	  ] .
	  FILTER langMatches(lang(?abstract),"en")
	  VALUES ?name { %s }
	}"""%(param)
	print(query)
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	return pd.json_normalize(results['results']['bindings'])


def lay_terms_from_redirect_and_wikilink():
	for obj in wikimed.find():
		if 'wiki_url' in obj.keys() and 'sct' in obj.keys():
			if 'redirect' not in obj.keys() and 'inlinks' not in obj.keys(): 
				itemLabel = obj['itemLabel'].capitalize()
				print(itemLabel)
				wiki_redirects = get_redirect(itemLabel)
				wiki_inlinks = get_wikilinks(itemLabel)
				if wiki_redirects != 0:
					obj['rn'] = wiki_redirects
				if wiki_inlinks != 0:
					obj['inlink'] = wiki_inlinks

				wikimed.update_one({'item':obj['item']},{"$set":{
						'redirect':wiki_redirects, 'inlinks':wiki_inlinks}}
						)

def get_wiki_abstract():
	wiki_titles = []
	for obj in wikimed.find():
		if 'sct' in obj.keys() and 'wiki_url' in obj.keys():
			if 'abstract' not in obj.keys():
				wiki_titles.append(obj['itemLabel'].capitalize())
	
	COUNTER = 0
	BATCH_SIZE = 100
	batch_wikis =''


	for wiki in wiki_titles:
		COUNTER +=1

		batch_wikis = batch_wikis +'"'+wiki+'"'+'@en'+'\n'

		if COUNTER % BATCH_SIZE == 0:
			print(COUNTER)
			results = abstract_query(batch_wikis)
			for index, row in results.iterrows():
				itemLabel = row['name.value']
				abstract = row['abstract.value']
				wikimed.update_one({'itemLabel':itemLabel.lower()},{"$set":{'abstract':abstract}
					})
			batch_wikis =''

	res = abstract_query(batch_wikis)

	for index, row in res.iterrows():
		temLabel = row['name.value']
		abstract = row['abstract.value']
		wikimed.update_one({'itemLabel':itemLabel.lower()},{"$set":{'abstract':abstract}
		})

def update_mongo_w_abstract(results):
	for batch in results:
		for i in range(len(batch)):
			itemLabel = batch.loc[i, 'name.value']
			wikimed.update_one({'itemLabel':batch.loc[i, 'name.value'].lower()},{"$set":{'abstract':batch.loc[i, 'abstract.value']}
				})

def get_abstract_from_wiki_api():
	
	wiki_itemLabel = []
	wiki_url = []
	for d in wikimed.find():
		if 'sct' in d.keys() and'wiki_url' in d.keys() and 'abstract' not in d.keys():
			wiki_itemLabel.append(d['itemLabel'])
			url = unquote(d['wiki_url']).split('/')[-1].replace('_',' ')
			wiki_url.append(url)
	
	for i, wiki in enumerate(wiki_url):
		itemLabel = wiki_itemLabel[i]
		print(itemLabel)
		abstract = ''
		try:
			abstract = wikipedia.summary('"'+wiki+'"')
			wikimed.update_one({'itemLabel':itemLabel},{"$set":{'abstract':abstract, 'abs_source':'wikiAPI'}})
		except wikipedia.exceptions.PageError as err:
			print("Error: {0}".format(err))




#lay_terms_from_redirect_and_wikilink()
# print('Get abstract from dbpedia')
# get_wiki_abstract()
print('Get abstract from wikipedia API')
get_abstract_from_wiki_api()
