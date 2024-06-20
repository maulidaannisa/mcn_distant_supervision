import os
import csv

def read_lines_from_file(filename, encodings=['utf-8', 'ISO-8859-1']):
    """Read lines from a text file with specified encodings."""
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as file:
                return file.readlines()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Failed to decode file: {filename}")

def get_labels_from_data(dir_path, csv_delimiter=None, file_prefixes=['train','dev', 'test']):
    labels = set()
    terms = set()
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if any(file.startswith(prefix) for prefix in file_prefixes):
                file_path = os.path.join(root, file)
                if csv_delimiter:
                    with open(file_path, 'r') as csvfile:
                        reader = csv.reader(csvfile, delimiter=csv_delimiter)
                        header = next(reader)
                        for row in reader:
                            label = '__label__{}'.format(row[3])
                            labels.add(label)
                else:
                    data = read_lines_from_file(file_path)
                    # print(data)
                    for line in data:
                        label = line.split()[0]
                        labels.add(label)
                        # term = ' '.join(word for word in line.split()[1:])
                        # print(term)
                        # terms.add(term.lower())
    # return labels, terms
    return labels

def get_labels_from_distant_data(file_path):
    return get_labels_from_data(os.path.dirname(file_path), file_prefixes=[os.path.basename(file_path)])

# Directories
mcn_data_dir = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/medical-entity-linking/distant_supervision/mcn_data'
psytar_dir = os.path.join(mcn_data_dir, 'psytar/')
cadec_dir = os.path.join(mcn_data_dir, 'cadec/')
cometa_dir = os.path.join(mcn_data_dir, 'cometa/stratified_general')

# Train and Test Data Labels
psytar_labels = get_labels_from_data(psytar_dir)
print(len(psytar_labels))
cadec_labels = get_labels_from_data(cadec_dir)
print(len(cadec_labels))
cometa_labels = get_labels_from_data(cometa_dir, csv_delimiter='\t')
print(len(cometa_labels))

# Union of Train and Test Data Labels
union_train_test_labels = set(psytar_labels.union(cadec_labels,cometa_labels))
print(len(union_train_test_labels))

# Distant Data Files
fs_file = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/medical-entity-linking/upload-to-github/distant-supervision/data/data_distant/mcn_distant-all-MiniLM-L6-v2-80.0.txt'
ir_file = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/medical-entity-linking/upload-to-github/distant-supervision/data/data_distant/mcn_data_inlink_re.txt'

# Distant Data Labels
fs_labels = get_labels_from_distant_data(fs_file)
# fs_labels, fs_terms = get_labels_from_distant_data(fs_file)


ir_labels = get_labels_from_distant_data(ir_file)
# ir_labels, ir_terms  = get_labels_from_distant_data(ir_file)


# Union of Distant Data Labels
union_distant_labels = set(fs_labels.union(ir_labels))
# union_distant_terms = set(fs_terms.union(ir_terms))
print(len(union_distant_labels))
# print(len(union_distant_terms))

# Intersection
intersection_labels = union_train_test_labels.intersection(union_distant_labels)
print(len(intersection_labels))
# Output
print(f"Number of Intersection of Train/Test and Distant Data Labels: {len(intersection_labels)}")
