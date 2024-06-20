import csv
import os

COMETA_DIR = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/MCN DATASETS/COMETA/'
MCN_DIR = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/medical-entity-linking/DATA_AUGMENTATION/upload-to-github/data-augmentation/mcn_data/'
psytar_dir = os.path.join(mcn_data_dir,'psytar')
cadec_dir = os.path.join(mcn_data_dir,'cadec')
cometa_dir = os.path.join(mcn_data_dir,'cometa')
fs_file = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/medical-entity-linking/distant_supervision/distant_data/mcn-sim-result/mcn_distant-all-MiniLM-L6-v2-80.0.txt'
ir_file = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/medical-entity-linking/distant_supervision/distant_data/mcn_data_inlink_re.txt'




def open_txt_file(filename):
	with open (filename,'r') as fs_file:
		data = fs_file.readlines()

	return data

def get_cometa_label(filename):
	cometa_labels = set()
	with open(filename, 'r') as csvfile:
			cometareader = csv.reader(csvfile, delimiter='\t')
			header = next(cometareader)
			for row in cometareader:
				cometa_labels.add(row[3])

	return cometa_labels

def get_label(entity):
	label = entity.split(' ')[0]
	sct_code = label[9:]

	return sct_code

def get_overlap_labels(fs_file, mcn_dir, data_name=None):
	fs_ire_concepts = set()

	data = open_txt_file(fs_file)
	
	for d in data:
		sct_code = get_label(d)
		fs_ire_concepts.add(sct_code)

	ire_file = 'mcn_data_inlink_re.txt'
	ire_data = open_txt_file(ire_file)

	for ire in ire_data:
		sct_code = get_label(ire)
		fs_ire_concepts.add(sct_code)
	print(len(fs_ire_concepts))

	if data_name == 'cometa':
		cmt_concepts = set()
		for file in os.listdir(mcn_dir):
			cometa_labels = set()
			filename = os.path.join(mcn_dir,file)
			cometa_labels = get_cometa_label(filename)

			cmt_concepts.update(cometa_labels)
		
		label = fs_ire_concepts.intersection(cmt_concepts)

	if data_name == 'cadec' or data_name == 'psytar':
		mcn_concepts = set()
		for file in os.listdir(mcn_dir):
			print(file)
			filename = os.path.join(mcn_dir,file)
			mcn_data = open_txt_file(filename)
			for data in mcn_data:
				mcn_code = get_label(data)
				mcn_concepts.add(mcn_code)

		label = fs_ire_concepts.intersection(mcn_concepts)

	return label

def create_distant_train_set(fs_file, label):
	flair_label_format = []
	for l in label:
		flair_label_format.append('__label__{}'.format(l))
	
	train_set = []
	data = open_txt_file(fs_file)
	for d in data:
		lbl = d.split(' ')[0]
		if lbl in flair_label_format:
			train_set.append(d)

	ir_file = 'mcn_data_inlink_re.txt'
	ir_data = open_txt_file(ir_file)
	for ir in ir_data:
		lbl = ir.split(' ')[0]
		if lbl in flair_label_format:
			train_set.append(ir)
	#print(len(train_set))
	return train_set

def create_distant_with_ori_train_set(fs_file, ori_dir, label, data_name=None):
	distant_train_set = create_distant_train_set(fs_file, label)

	flair_label_format = []
	for l in label:
		flair_label_format.append('__label__{}'.format(l))

	if data_name=='cometa':
		existing_train_set = []
		for file in os. listdir(ori_dir): 
			if file == 'test.csv' or file == 'dev.csv':
				continue
			else:
				with open(os.path.join(ori_dir, file), 'r') as csvfile:
					cometareader = csv.reader(csvfile, delimiter='\t')
					header = next(cometareader)
					for row in cometareader:
						if row[3] in list(label):
							entity = '__label__{}'.format(row[3])+' '+ row[1]+'\n'
							existing_train_set.append(entity)
	
	if data_name == 'psytar':
		existing_train_set = []

		for file in os.listdir(ori_dir):
			if file == 'test_data.txt' or file == 'dev_data.txt':
				continue
			else:
				ex_train_data = open_txt_file(os.path.join(ori_dir,file))
				for tr in ex_train_data:
					lbl = tr.split(' ')[0]
					if lbl in flair_label_format:
						existing_train_set.append(tr)
	
	if data_name == 'cadec':
		existing_train_set = []
		for file in os.listdir(ori_dir):
			if file.startswith('train'):
				cad_train_data = open_txt_file(os.path.join(ori_dir,file))
				for cad in cad_train_data:
					lbl = cad.split(' ')[0]
					if lbl in flair_label_format:
						existing_train_set.append(cad)
			else:
				continue

	train_set_combined = distant_train_set + existing_train_set
	# print(len(distant_train_set))
	# print(len(train_set_combined))
	# print(len(existing_train_set))
	return train_set_combined, existing_train_set


def create_dev_test_set(data_dir, label, data_name=None):
	if data_name =='cometa':
		test_set = []
		dev_set = []
		for file in os.listdir(data_dir):
			if file == 'train.csv':
				continue
			elif file=='test.csv':
				with open(os.path.join(data_dir,file),'r') as csvfile:
					cometareader = csv.reader(csvfile, delimiter='\t')
					header = next(cometareader)
					for row in cometareader:
						if row[3] in list(label):
							entity = '__label__{}'.format(row[3])+' '+row[1]
							test_set.append(entity)
			else:
				with open(os.path.join(data_dir,file),'r') as csvfile:
					cometareader = csv.reader(csvfile, delimiter='\t')
					header = next(cometareader)
					for row in cometareader:
						if row[3] in list(label):
							entity = '__label__{}'.format(row[3])+' '+row[1]
							dev_set.append(entity)

	if data_name == 'psytar':
		test_set = []
		dev_set = []
		flair_label_format = []
		for l in label:
			flair_label_format.append('__label__{}'.format(l))

		for file in os.listdir(data_dir):
			if file == 'train_data.txt':
				continue
			elif file == 'test_data.txt':
				test_data = open_txt_file(os.path.join(data_dir,file))
				for d in test_data:
					lbl = d.split(' ')[0]
					if lbl in flair_label_format:
						test_set.append(d)
			else:
				dev_data = open_txt_file(os.path.join(data_dir,file))
				for d in dev_data:
					lbl = d.split(' ')[0]
					if lbl in flair_label_format:
						dev_set.append(d)
	
	if data_name == 'cadec':
		test_set = []
		dev_set = []
		flair_label_format = []
		for l in label:
			flair_label_format.append('__label__{}'.format(l))
		for file in os.listdir(data_dir):
			if file.startswith('train'):
				continue
			else:
				data = open_txt_file(os.path.join(data_dir,file))
				for d in data:
					lbl = d.split(' ')[0]
					if lbl in flair_label_format:
						test_set.append(d)

	# print(len(dev_set))
	# print(len(test_set))

	return dev_set, test_set


# # Constants
# FS_DIR = '/path/to/mcn-sim-result'
# COMETA_DIR = '/path/to/cometa'
# MCN_DIR = '/path/to/mcn_data'

def process_cometa_dataset(fs_path, cometa_subdir):
    """Process Cometa dataset and create respective data sets."""
    label = get_overlap_labels(fs_path, cometa_subdir, data_name='cometa')
    print(f"Cometa Labels: {len(label)}")

    union_train_set, existing_train_set = create_distant_with_ori_train_set(fs_path, cometa_subdir, label, data_name='cometa')
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

def save_data_set(directory, filename, data_set):
    """Save a data set to a file."""
    with open(os.path.join(directory, filename), 'w') as file:
        file.writelines('\n'.join(data_set))

def main():
    filename = 'mcn_distant-all-MiniLM-L6-v2-80.0.txt'
    fs_path = os.path.join(FS_DIR, filename)

    cometa_subdir = os.path.join(COMETA_DIR, 'stratified_general')
    process_cometa_dataset(fs_path, cometa_subdir)

    cadec_dir = os.path.join(MCN_DIR, 'cadec/fold/')
    process_cadec_dataset(fs_path, cadec_dir)

if __name__ == "__main__":
    main()



