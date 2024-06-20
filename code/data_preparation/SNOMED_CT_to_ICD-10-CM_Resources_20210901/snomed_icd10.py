import csv
import json
from Levenshtein import distance as lev

class SnomedMapping:

    def __init__(self):
        self.build_snomed_code_to_label()
        self.build_icd_to_snomed()


    def map_icd_to_snomed(self, icd_code, snomed_code):
        if icd_code not in self.icd_to_snomed:
            self.icd_to_snomed[icd_code] = [snomed_code]
        else:
            if snomed_code not in self.icd_to_snomed[icd_code]:
                self.icd_to_snomed[icd_code].append(snomed_code)

    def build_snomed_code_to_label(self):
        self.snomed_code_to_label = {}

        # hasil export MongoDB
        filepath = "preprocessed_snomed.csv"
        with open(filepath, 'r', encoding="utf-8") as csvfile:
            rdr = csv.reader(csvfile, delimiter=',')
            next(rdr, None) # skip header
            for rd in rdr:
                snomed_code = rd[-1]
                snomed_name = rd[1].replace("(%s)".format(rd[-2]), "").strip()

                self.snomed_code_to_label[snomed_code] = snomed_name

    def build_icd_to_snomed(self):
        self.icd_to_snomed = {}

        # build icd_to_snomed based on two files

        # FILE 1 from NLM
        # https://www.nlm.nih.gov/healthit/snomedct/us_edition.html
        filepath_1 = "tls_Icd10cmHumanReadableMap_US1000124_20210901.tsv"
        with open(filepath_1, 'r', encoding="utf-8") as tsvfile:
            rdr = csv.reader(tsvfile, delimiter='\t')
            next(rdr, None) # skip header
            for rd in rdr:
                icd_code = rd[11]
                snomed_code = rd[5]
                snomed_name = rd[6]

                if len(icd_code) > 0:
                    self.map_icd_to_snomed(icd_code, snomed_code)

                    # file distributed by NLM have the snomed name
                    # since this is the latest file, we can use this to override the dictionary
                    self.snomed_code_to_label[snomed_code] = snomed_name

        # FILE 2 from MedCat
        filepath_2 = "icd10_snomed.json"
        with open(filepath_2, 'r', encoding="utf-8") as icdfile:
            data = json.load(icdfile)
            for snomed_code, icd_codes in data.items():
                for icd_code in icd_codes:
                    self.map_icd_to_snomed(icd_code, snomed_code)

    def get_snomed_by_icd(self, icd_code):
        if icd_code not in self.icd_to_snomed:
            return "Not Found"

        return self.icd_to_snomed[icd_code]


    def get_best_snomed_by_icd(self, icd_code, string_match):
        # best = shortest/smallest Lev Distance

        if icd_code not in self.icd_to_snomed:
            return "Not Found"

        snomed_codes = self.icd_to_snomed[icd_code]
        # if only 1 snomed code just return it
        if len(snomed_codes) == 1:
            return snomed_codes[0]

        # if more than 1 calculcate the shortest distance

        shortest = 99999
        best_snomed_code = None
        for snomed_code in snomed_codes:
            # if the snomed code not in the dictionary we can't make a string matching
            if snomed_code not in self.snomed_code_to_label:
                continue

            snomed_name = self.snomed_code_to_label[snomed_code]
            lev_dist = lev(string_match, snomed_name)
            if lev_dist < shortest:
                shortest = lev_dist
                best_snomed_code = snomed_code

        if best_snomed_code:
            return best_snomed_code
        else:
            return snomed_codes


snm = SnomedMapping()

i = 1
# Try From JSON Wiki
with open("wikimed.json", "r", encoding="utf-8") as read_file:
    data = json.load(read_file)
    for d in data:
        if "icd" in d and "sct" not in d:
            for icd in d["icd"]:
                print(["icd"], len(d["icd"]))
                for icd in d["icd"]:
                    print(snm.get_best_snomed_by_icd(icd, d["itemLabel"]))


