# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT DISTINCT ?item ?itemLabel ?identifier ?wiki_url WHERE {
  {
    SELECT ?item ?itemLabel (?sct AS ?identifier) ?wiki_url WHERE {
      ?item wdt:P5806 ?sct.
      OPTIONAL {
        ?wiki_url schema:about ?item .
        ?wiki_url schema:inLanguage "en" .
        FILTER (SUBSTR(str(?wiki_url), 1, 25) = "https://en.wikipedia.org/")
      }
      SERVICE wikibase:label {
        bd:serviceParam wikibase:language "en".
        ?item rdfs:label ?itemLabel.
      }
    }
  } UNION
  {
    SELECT ?item ?itemLabel (?cui AS ?identifier) ?wiki_url WHERE {
      ?item wdt:P2892 ?cui.
      OPTIONAL {
        ?wiki_url schema:about ?item .
        ?wiki_url schema:inLanguage "en" .
        FILTER (SUBSTR(str(?wiki_url), 1, 25) = "https://en.wikipedia.org/")
      }
      SERVICE wikibase:label {
        bd:serviceParam wikibase:language "en".
        ?item rdfs:label ?itemLabel.
      }
    }
  } UNION
  {
    SELECT ?item ?itemLabel (?icd AS ?identifier) ?wiki_url WHERE {
      ?item wdt:P494 ?icd.
      OPTIONAL {
        ?wiki_url schema:about ?item .
        ?wiki_url schema:inLanguage "en" .
        FILTER (SUBSTR(str(?wiki_url), 1, 25) = "https://en.wikipedia.org/")
      }
      SERVICE wikibase:label {
        bd:serviceParam wikibase:language "en".
        ?item rdfs:label ?itemLabel.
      }
    }
  }
}
"""


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


results = get_results(endpoint_url, query)

for result in results["results"]["bindings"]:
    print(result)
