from trec_car import read_data
from tqdm import tqdm

from pymongo import MongoClient
client = MongoClient()

# print("Start Inserting Redirect Links")
# db = client.wiki_redirect
# content = db.redirects

data = []
COUNTER = 0
BATCH_SIZE = 10000

with open('/Volumes/AN-SSD/Doctoral/car-wiki2020-01-01//enwiki2020.cbor', 'rb') as f:
    for article in tqdm(read_data.iter_annotations(f)):
        if article.page_meta.redirectNames:
            COUNTER += 1
            for word in article.page_meta.redirectNames:
                data.append({
                    'redirect_link': word,
                    'title': article.page_name.strip()
                })

            if COUNTER % BATCH_SIZE == 0:
                print("Inserting...")
                content.insert_many(data)
                data = []

    content.insert_many(data)


print("Creating Index Redirect")
content.create_index("redirect_link")

# ==============================================================

print("Start Inserting Inlinks")
db = client.wiki_inlink
content = db.inlinks

data = []
COUNTER = 0

with open('/Volumes/AN-SSD/Doctoral/car-wiki2020-01-01/enwiki2020.cbor', 'rb') as f:
    for article in tqdm(read_data.iter_annotations(f)):
        if article.page_meta.inlinkAnchors:
            COUNTER += 1

            if article.page_meta.inlinkAnchors:
                for (word, freq) in article.page_meta.inlinkAnchors:
                    data.append({
                        'inlink': word,
                        'title': article.page_name.strip(),
                        'freq': freq
                    })

            if COUNTER % BATCH_SIZE == 0:
                print("Inserting...")
                content.insert_many(data)
                data = []

    content.insert_many(data)


print("Creating Index Inlink")
content.create_index("inlink")
