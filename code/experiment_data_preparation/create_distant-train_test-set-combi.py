import csv
import os

mcn_data_dir = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/medical-entity-linking/distant_supervision/mcn_data'

def open_txt_file(filename):
	with open (filename,'r') as fs_file:
		data = fs_file.readlines()

	return data


def get_psytar_test_set(psytar_dir):
	pystar_test_set = []
	test_data = open_txt_file(os.path.join(psytar_dir,'test_data.txt'))
	for d in test_data:
		pystar_test_set.append(d)
	return set(pystar_test_set)

def get_cadec_test_set(cadec_dir):
	cadec_test_set = set()
	for idx in range(5):
		fold_path = os.path.join(cadec_dir, str(idx))
		for file in os.listdir(fold_path):
			if file.startswith('test'):
				data = open_txt_file(os.path.join(fold_path,file))
				for d in data:
					cadec_test_set.add(d)
	return cadec_test_set

def get_cometa_test_set(cometa_dir):
	cometa_test_set = set()
	sct_type = ['stratified_general', 'stratified_specific']
	for typ in sct_type:
		if typ=='stratified_specific':
			continue
		with open(os.path.join(os.path.join(cometa_dir,typ),'test.csv'),'r') as csvfile:
			cometareader = csv.reader(csvfile, delimiter='\t')
			header = next(cometareader)
			for row in cometareader:
				entity = '__label__{}'.format(row[3])+' '+row[1]
				cometa_test_set.add(entity)
	return cometa_test_set

def get_cadec_labels(cadec_dir):
	cadec_set = set()
	for idx in range(5):
		fold_path = os.path.join(cadec_dir, str(idx))
		for file in os.listdir(fold_path):
			#if file.startswith('test'):
			data = open_txt_file(os.path.join(fold_path,file))
			for d in data:
				cadec_set.add(d)
	return cadec_set

def get_cometa_labels(cometa_dir):
	cometa_set = set()
	sct_type = ['stratified_general', 'stratified_specific']
	for typ in sct_type:
		if typ == 'stratified_specific':
			continue
		for file in os.listdir(os.path.join(cometa_dir,typ)):
			with open(os.path.join(os.path.join(cometa_dir,typ),file),'r') as csvfile:
				cometareader = csv.reader(csvfile, delimiter='\t')
				header = next(cometareader)
				for row in cometareader:
					entity = '__label__{}'.format(row[3])+' '+row[1]
					cometa_set.add(entity)
	return cometa_set

def get_psytar_labels(psytar_dir):
	pystar_set = set()
	for file in os.listdir(psytar_dir):
		test_data = open_txt_file(os.path.join(psytar_dir,file))
		for d in test_data:
			pystar_set.add(d)
		return pystar_set

#combined test set from cadec, psytar and cometa
def joined_test_set(psytar_dir, cadec_dir, cometa_dir):
	pystar_test_set = list(get_psytar_labels(psytar_dir))
	cadec_test_set = list(get_cadec_labels(cadec_dir))
	cometa_test_set = list(get_cometa_labels(cometa_dir))
	print('psytar = ', len(pystar_test_set))
	print('cadec = ', len(cadec_test_set))
	print('cometa = ', len(cometa_test_set))

	joined_test_set = pystar_test_set + cadec_test_set + cometa_test_set

	return set(joined_test_set)

def all_distant_train_set(fs_file, ir_file):
	fs_data = open_txt_file(fs_file)
	ir_data = open_txt_file(ir_file)

	all_distant_train_set = fs_data + ir_data
	
	return all_distant_train_set

def get_overlap_labels(joined_test_set, all_distant_train_set):

	unique_joined_test_labels = set()
	for ts in joined_test_set:
		ts_label = ts.split()[0]
		unique_joined_test_labels.add(ts_label)
	print('unique_joined_test_labels',len(unique_joined_test_labels))
	unique_ds_labels = set()
	for ds in all_distant_train_set:
		ds_label = ds.split()[0]
		unique_ds_labels.add(ds_label)
	print('unique_ds_labels', len(unique_ds_labels))
	ovelap_labels = unique_ds_labels.intersection(unique_joined_test_labels)
	return ovelap_labels

def get_filtered_joined_test_set(joined_test_set, overlap_labels):

	filtered_joined_test_set = []
	for ts_data in joined_test_set:
		ts_lbl = ts_data.split()[0]
		if ts_lbl in list(overlap_labels):
			filtered_joined_test_set.append(ts_data+'\n')
	#print('filtered_join_test',len(filtered_joined_test_set))
	return filtered_joined_test_set

def write_file(filename, list_of_data):
	with open (filename,'w') as file:
		for d in list_of_data:
			file.writelines(d)


psytar_dir = os.path.join(mcn_data_dir,'psytar')
cadec_dir = os.path.join(mcn_data_dir,'cadec')
cometa_dir = os.path.join(mcn_data_dir,'cometa')
fs_file = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/medical-entity-linking/distant_supervision/distant_data/mcn-sim-result/mcn_distant-all-MiniLM-L6-v2-80.0.txt'
ir_file = '/Users/annisaningtyas/Documents/KULIAH S3/CODE AND DATASETS/medical-entity-linking/distant_supervision/distant_data/mcn_data_inlink_re.txt'

joined_test_set = joined_test_set(psytar_dir, cadec_dir, cometa_dir)
# print('join_test', len(joined_test_set))

all_distant_train_set = all_distant_train_set(fs_file,ir_file)
print('all_distant data', len(all_distant_train_set))

overlap_labels = get_overlap_labels(joined_test_set,all_distant_train_set)
print('overlap label', len(overlap_labels))

filtered_joined_test_set = get_filtered_joined_test_set(joined_test_set, overlap_labels)
print('filtered_join_test', len(filtered_joined_test_set))


# write_file('all_distant_data.txt', all_distant_train_set)
# write_file('overlap_joined_test_set.txt', filtered_joined_test_set)


		





