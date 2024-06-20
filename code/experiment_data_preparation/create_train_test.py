import csv
import os

# Constants
COMETA_DIR = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/MCN DATASETS/COMETA/'
MCN_DIR = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/medical-entity-linking/DATA_AUGMENTATION/upload-to-github/data-augmentation/mcn_data/'
DS_DIR = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/medical-entity-linking/upload-to-github/distant-supervision/data/data_distant'

def read_lines_from_file(filename):
    """Read lines from a text file with fallback encodings."""
    for encoding in ['utf-8', 'ISO-8859-1', 'cp1252', 'utf-16']:
        try:
            with open(filename, 'r', encoding=encoding) as file:
                return file.readlines()
        except UnicodeDecodeError:
            continue
    raise Exception(f"Could not read file {filename} with common encodings.")

def read_csv(filename, delimiter='\t'):
    """Read a CSV file and return its rows."""
    with open(filename, 'r') as csvfile:
        return list(csv.reader(csvfile, delimiter=delimiter))

def extract_labels_from_csv(rows, label_col=3):
    """Extract labels from CSV rows."""
    return {row[label_col] for row in rows[1:]}  # Skipping header

def get_sct_code_from_entity(entity):
    """Extract SCT code from an entity string."""
    return entity.split(' ')[0][9:]

def get_overlap_labels(fs_file, mcn_dir, data_name=None):
    """Get overlapping labels from files."""
    fs_ire_concepts = {get_sct_code_from_entity(d) for d in read_lines_from_file(fs_file)}

    ire_file = os.path.join(DS_DIR, 'mcn_data_inlink_re.txt')
    ire_data = read_lines_from_file(ire_file)
    fs_ire_concepts.update(get_sct_code_from_entity(ire) for ire in ire_data)

    if data_name == 'cometa':
        cmt_concepts = set()
        for file in os.listdir(mcn_dir):
            filename = os.path.join(mcn_dir, file)
            cometa_labels = extract_labels_from_csv(read_csv(filename))
            cmt_concepts.update(cometa_labels)
        return fs_ire_concepts.intersection(cmt_concepts)

    if data_name in ['cadec', 'psytar']:
        mcn_concepts = set()
        for file in os.listdir(mcn_dir):
            print(file)
            filename = os.path.join(mcn_dir, file)
            mcn_data = read_lines_from_file(filename)
            mcn_concepts.update(get_sct_code_from_entity(data) for data in mcn_data)
        return fs_ire_concepts.intersection(mcn_concepts)

    return set()

# Rest of the refactored functions

def create_flair_labels(label_set):
    """Create FLAIR label formats for a set of labels."""
    return ['__label__{}'.format(l) for l in label_set]

def create_distant_train_set(fs_file, label_set):
    """Create a training set with distant labels."""
    flair_labels = create_flair_labels(label_set)
    train_set = []

    for line in read_lines_from_file(fs_file):
        if line.split(' ')[0] in flair_labels:
            train_set.append(line)

    ir_file = os.path.join(DS_DIR, 'mcn_data_inlink_re.txt')
    ir_data = read_lines_from_file(ir_file)

    for ir in ir_data:
        if ir.split(' ')[0] in flair_labels:
            train_set.append(ir)

    return train_set

def create_combined_train_set(fs_file, ori_dir, label_set, data_name=None):
    """Combine distant and original training sets."""
    distant_train_set = create_distant_train_set(fs_file, label_set)
    flair_labels = create_flair_labels(label_set)
    existing_train_set = []

    if data_name == 'cometa':
        for file in os.listdir(ori_dir):
            if file in ['test.csv', 'dev.csv']:
                continue
            rows = read_csv(os.path.join(ori_dir, file))
            for row in rows[1:]:
                if row[3] in label_set:
                    entity = '__label__{} {}'.format(row[3], row[1])
                    existing_train_set.append(entity)

    elif data_name == 'psytar':
        for file in os.listdir(ori_dir):
            if file in ['test_data.txt', 'dev_data.txt']:
                continue
            ex_train_data = read_lines_from_file(os.path.join(ori_dir, file))
            for tr in ex_train_data:
                if tr.split(' ')[0] in flair_labels:
                    existing_train_set.append(tr)

    elif data_name == 'cadec':
        for file in os.listdir(ori_dir):
            if file.startswith('train'):
                cad_train_data = read_lines_from_file(os.path.join(ori_dir, file))
                for cad in cad_train_data:
                    if cad.split(' ')[0] in flair_labels:
                        existing_train_set.append(cad)

    return distant_train_set + existing_train_set, existing_train_set

def create_dev_test_set(data_dir, label_set, data_name=None):
    """Create development and test sets."""
    dev_set, test_set = [], []
    flair_labels = create_flair_labels(label_set)

    if data_name == 'cometa':
        for file in os.listdir(data_dir):
            if file == 'train.csv':
                continue
            rows = read_csv(os.path.join(data_dir, file))
            for row in rows[1:]:
                if row[3] in label_set:
                    entity = '__label__{} {}'.format(row[3], row[1])
                    (test_set if file == 'test.csv' else dev_set).append(entity)

    elif data_name == 'psytar':
        for file in os.listdir(data_dir):
            if file == 'train_data.txt':
                continue
            data = read_lines_from_file(os.path.join(data_dir, file))
            for d in data:
                if d.split(' ')[0] in flair_labels:
                    (test_set if file == 'test_data.txt' else dev_set).append(d)

    elif data_name == 'cadec':
        for file in os.listdir(data_dir):
            if not file.startswith('train'):
                data = read_lines_from_file(os.path.join(data_dir, file))
                for d in data:
                    if d.split(' ')[0] in flair_labels:
                        (test_set if 'test' in file else dev_set).append(d)

    return dev_set, test_set


def process_cometa_dataset(fs_path, cometa_subdir):
    """Process Cometa dataset and create respective data sets."""
    label = get_overlap_labels(fs_path, cometa_subdir, data_name='cometa')
    print(f"Cometa Labels: {len(label)}")

    union_train_set, existing_train_set = create_combined_train_set(fs_path, cometa_subdir, label, data_name='cometa')
    print(f"Union Train Set Size: {len(union_train_set)}")

    dev_set, test_set = create_dev_test_set(cometa_subdir, label, data_name='cometa')

    subfolder_name = 'train_fs-ire_' + fs_path.split('_')[1].split('.txt')[0] + '_stratified_general'
    cometa_output_dir = os.path.join('DISTANT_WITH_ORI/cometa', subfolder_name)
    os.makedirs(cometa_output_dir, exist_ok=True)

    save_data_set(cometa_output_dir, 'train_data.txt', union_train_set)
    save_data_set(cometa_output_dir, 'dev_data.txt', dev_set)
    save_data_set(cometa_output_dir, 'test_data.txt', test_set)

def process_cadec_dataset(fs_path, cadec_dir):
    """Process Cadec dataset for each fold and create respective data sets."""
    for idx in range(5):
        fold_path = os.path.join(cadec_dir, str(idx))
        label = get_overlap_labels(fs_path, fold_path, data_name='cadec')
        print(f"Cadec Labels for fold {idx}: {len(label)}")

        train_set = create_distant_train_set(fs_path, label)
        dev_set, test_set = create_dev_test_set(fold_path, label, data_name='cadec')

        subfolder_name = 'train_fs-ire_' + fs_path.split('_')[1].split('.txt')[0]
        cadec_output_dir = os.path.join('DISTANT_ONLY/cadec', subfolder_name, str(idx))
        os.makedirs(cadec_output_dir, exist_ok=True)

        save_data_set(cadec_output_dir, 'train_data.txt', train_set)
        save_data_set(cadec_output_dir, 'dev_data.txt', dev_set)
        save_data_set(cadec_output_dir, 'test_data.txt', test_set)

def process_psytar_dataset(fs_path, psytar_dir):
    """Process Psytar dataset and create respective data sets."""
    label = get_overlap_labels(fs_path, psytar_dir, data_name='psytar')
    print(f"Psytar Labels: {len(label)}")

    union_train_set, existing_train_set = create_combined_train_set(fs_path, psytar_dir, label, data_name='psytar')
    print(f"Union Train Set Size: {len(union_train_set)}")

    dev_set, test_set = create_dev_test_set(psytar_dir, label, data_name='psytar')

    subfolder_name = 'train_fs-ire_' + fs_path.split('_')[1].split('.txt')[0] + '_psytar'
    psytar_output_dir = os.path.join('DISTANT_WITH_ORI/psytar', subfolder_name)
    os.makedirs(psytar_output_dir, exist_ok=True)

    save_data_set(psytar_output_dir, 'train_data.txt', union_train_set)
    save_data_set(psytar_output_dir, 'dev_data.txt', dev_set)
    save_data_set(psytar_output_dir, 'test_data.txt', test_set)

def save_data_set(directory, filename, data_set):
    """Save a data set to a file."""
    with open(os.path.join(directory, filename), 'w') as file:
        file.writelines(''.join(data_set))

def main():
    filename = 'mcn_distant-all-MiniLM-L6-v2-80.0.txt'
    fs_path = os.path.join(DS_DIR, filename)

    cometa_subdir = os.path.join(COMETA_DIR, 'stratified_general')
    process_cometa_dataset(fs_path, cometa_subdir)

    cadec_dir = os.path.join(MCN_DIR, 'cadec/fold/')
    process_cadec_dataset(fs_path, cadec_dir)

    psytar_dir = os.path.join(MCN_DIR, 'psytar/data')
    process_psytar_dataset(fs_path, psytar_dir)

if __name__ == "__main__":
    main()


