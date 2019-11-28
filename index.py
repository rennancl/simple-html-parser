import json
import os
import threading
from multiprocessing.dummy import Pool as ThreadPool
import subprocess
import sys
import requests

# INPUT REQUIREMENT: Folder with authors and pubs data in JSON format. 
# Each folder should have multiple files with one instance per line in each file.
files_dir = 'jsons/groups/'

files_to_index = [fname for fname in os.listdir(files_dir) if fname.startswith('part-')]

files = []

def index_data(bulk_data_path, index_url='http://localhost:9200/lattes/'):
        bashCommand = ' cat {0} | parallel --pipe -L 2 -N 2000 -j3 \'curl -s -H \'Content-Type:application/json\' {1} --data-binary @- > /dev/null \' '.format(bulk_data_path, index_url+'_bulk')
        output = subprocess.run(['bash','-c', bashCommand], stderr=sys.stderr, stdout=sys.stdout)

# Create index called Lattes
requests.delete('http://localhost:9200/lattes/').json()

with open('config/settings.json') as f:
        my_settings = f.read()
with open('config/mappings.json') as f:
        my_mappings = f.read()

res = requests.put('http://localhost:9200/lattes/', data = my_settings, headers={"Content-Type": "application/json"}).json()
if res['acknowledged'] == True:
        print("Índice \'lattes\' criado.")
else:
        print("Falha ao criar o índice \'lattes\'.")

# Update mapping
res = requests.put('http://localhost:9200/lattes/_mappings', data = my_mappings, headers={"Content-Type": "application/json"}).json()
if res['acknowledged'] == True:
        print("Mapping do Índice \'lattes\' criado com sucesso.")
else:
        print("Falha ao criar mapping para o índice \'lattes\'.")

# Authors
for fname in files_to_index:
        print('Files - Processing file {0}...'.format(fname))
        new_data = []
        inpath = authors_dir+fname
        out_path = 'bulk_data/authors/'+fname
        with open(inpath) as f:
                for line in f:
                        if len(line[:-1]) == 0:
                                continue
                        data = json.loads(line[:-1])
                        _id = data['id']
                        header = json.dumps({'index':{'_index': 'lattes', '_type':'_doc', '_id':_id}})
                        new_data.append(header)
                        new_data.append(line[:-1])
        with open(out_path, 'w') as out:
                for line in new_data:
                        out.write(line+'\n')

        files.append(out_path)

print('Indexing {} Files...'.format(len(files)))

# Launch threads to bulk index data
pool = ThreadPool(2)
results = pool.map(index_data, files)
pool.close()
pool.join()
