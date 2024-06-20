from trec_car import read_data
from tqdm import tqdm
import itertools
from pymongo import MongoClient
client = MongoClient()

print("Start Inserting Wikipedia Articles")
db = client.enwiki_cbor
content = db.enwiki_2020

data = []
COUNTER = 0
BATCH_SIZE = 10000

with open('/Volumes/AN-SSD/Doctoral/car-wiki2020-01-01/enwiki2020.cbor', 'rb') as f:
    for article in tqdm(read_data.iter_annotations(f)):
        if not type(article.page_type) is read_data.ArticlePage:
            continue

        COUNTER +=1
        
        # if COUNTER <=462633:
        #     continue
        
        inlinks = ''
        if article.page_meta.inlinkAnchors:
            inlinks = [word for (word, freq) in article.page_meta.inlinkAnchors]
        
        data.append({
            "_type": "article",
            "id": article.page_id,
            "title": article.page_name,
            "text": article.get_text(),
            "names": article.page_meta.redirectNames,
            "inlinks": inlinks,
            "redirects": article.page_meta.redirectNames,
            "categories": article.page_meta.categoryNames,
            "headings": [s.heading for s in itertools.chain.from_iterable(article.flat_headings_list())],
        })

        if COUNTER % BATCH_SIZE == 0:
            print("Inserting...")
            content.insert_many(data)
            data = []

    content.insert_many(data)

print("Creating Index..")
content.create_index("title")
content.create_index("categories")
content.create_index("inlinks")
content.create_index("redirects")