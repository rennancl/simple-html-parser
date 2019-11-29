import json
import sys
import glob, os
import pandas as pd
import uuid
from bs4 import BeautifulSoup

def norm_string(text):
    return text.lower().replace("\t", "").rstrip().replace(":", "")

def print_json(text):
    text = json.dumps(text, indent=4, sort_keys=True, ensure_ascii=False)
    print(text)


def open_and_load(file):
    with open(file, 'r') as f:
        htmltxt = f.read().replace('\n', '')
    soup = BeautifulSoup(htmltxt, 'lxml')
    return soup

def parse_about(soup):
    repercution = soup.findAll("div", {"id": "repercussao"})
    if repercution:
        return norm_string(str(repercution[0].contents[1].contents[5]).replace("</p>", "").replace("<p>", ""))

    return ""

def parse_id(soup):
    divs = soup.find_all('div', attrs={'style': 'text-align: center !important;'})
    try:
        id = str(divs[0])[80:125]
        id = id.split("/")[-1]
        return id
    except:
        return ""

def translate_keys(dictionary):
    translations = {"ano de formação": "year",
                    "bairro": "neighborhood",
                    "caixa postal": "mailbox",
                    "cep": "postcode",
                    "complemento": "complement",
                    "data da situação": "date",
                    "data do último envio": "updatedate",
                    "instituição do grupo": "institution",
                    "localidade": "locality",
                    "logradouro": "street",
                    "líder(es) do grupo": "leader",
                    "número": "number",
                    "situação do grupo": "situation",
                    "sub área": "subarea",
                    "telefone": "phone",
                    "uf": "state",
                    "unidade": "unit",
                    "área predominante": "area"
    }
    for key in translations:
        try:
            dictionary[translations[key]] = dictionary.pop(key)
        except:
            continue
    return dictionary

def parse(soup):
    att = soup.findAll("div", {"class": "control-group"})
    parsed = {}
    for at in att:
        try:
            parsed[norm_string(at.contents[0].contents[0])] = norm_string(at.contents[2].contents[0])
        except:
            continue
    
    parsed["id"] = parse_id(soup)
    parsed["uuid"] = str(uuid.uuid4())
    
    try:
        parsed["sub área"] = parsed.get("área predominante", "").split(";")[1][1:]
        parsed["área predominante"] =  parsed.get("área predominante", "").split(";")[0]
    except:
        parsed["sub área"] = ""
        parsed["área predominante"] = ""
    
    att = soup.findAll("h1", {"style": "position: relative;"})[0].contents[0]
    parsed["name"] = norm_string(str(att)[1:])
    parsed["about"] = parse_about(soup)
    parsed = translate_keys(parsed)
    parsed["doc_type"] = "institution"
    parsed["adress"] = dict()
    for key in ["neighborhood", "latitude", "longitude", "postcode", "street", "state", "locality", "number", "complement"]:
        parsed["adress"][key] = parsed.pop(key) 
    return parsed

def list_to_json(lis):
    doc = {}
    doc["name"] = lis[0]
    doc["formation"] = lis[1]
    doc["date"] = lis[2]
    doc["id"] = lis[3]
    doc["lattes_id"] = lis[4]
    return doc

def get_lattes_id():
    files = [file for file in glob.glob("*html") if 'p' in file]
    lis = []
    for file in files:
        try:
            att = open_and_load(file).findAll("div", {"id": "indicadoresProducao"})
            id_ = str(att[0].contents[5].contents[3].contents[0])[95:105]
            lis.append({"id_lattes": id_, "id_people":int(file.split("_")[1].split(".")[0])})
        except:
            continue
    return pd.DataFrame(lis)

def researchers_df():
    df_ids = get_lattes_id()
    columns = ["name","grad","date","to_drop","id_people","id"]
    people = pd.read_csv('./researcher_groups.csv', header=None, names=columns).dropna()
    people = people.merge(df_ids, on="id_people")
    people["id"] = people["id"].transform(lambda x: x.split("/")[-1]) 
    people = people.groupby('id')[["name", "grad", "date", "id_people", "id_lattes"]]
    people = people.apply(lambda x: x.values.tolist()).to_frame().reset_index()
    people.columns = ["id", "people"]
    people["people"] = people["people"].transform(lambda x: [list_to_json(i) for i in x]) 
    return people

def parse_all():
    files = [file for file in glob.glob("*html") if 'p' not in file]
    # must change this 10 in the files list to include all files it encountered
    groups = [open_and_load(file) for file in files[:10]]
    groups_ = []
    # passing the errors in this general way is not a good way to handle this, buts its the fastest way to implement
    # and i need it now...
    for g in groups:
        try:
            groups_.append(parse(g))
        except:
            continue
    groups = groups_ 
    df = pd.DataFrame(groups).merge(researchers_df(), on="id")
    return df

if __name__== "__main__":
    try:
        path = sys.argv[1]
    except:
        print("Don't forgot to pass the path as the second argument")
        sys.exit()

    path = os.path.abspath(path)    
    os.chdir(path)
    if not os.path.isdir("./institutions"):
        os.mkdir("./institutions")

    # should add an loop here to iterate throug all directories i want
    # (but for now ill use 1 for testing purpose) 
    for i in range(1, 51):
        os.chdir(path + "/" + str(i))

        jsons = json.loads(parse_all().to_json(orient='records'))

        os.chdir(path)
        out_path = "institutions/part-" + str(i) 
        with open(out_path, 'w') as out:
                for line in jsons:
                        out.write(json.dumps(line)+'\n')
                        # print_json(line)
