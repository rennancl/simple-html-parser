import json
import sys
import pandas as pd
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

    parsed["sub área"] = parsed["área predominante"].split(";")[1][1:]
    parsed["área predominante"] = parsed["área predominante"].split(";")[0]

    att = soup.findAll("h1", {"style": "position: relative;"})[0].contents[0]
    parsed["name"] = norm_string(str(att)[1:])
    parsed["about"] = parse_about(soup)
    parsed["id"] = parse_id(soup)
    parsed = translate_keys(parsed)

    parsed["adress"] = [] 
    for key in ["neighborhood", "latitude", "longitude", "postcode", "street", "state", "locality", "number", "complement"]:
        parsed["adress"].append(parsed.pop(key))
    
    return parsed


def list_to_json(lis):
    doc = {}
    doc["name"] = lis[0]
    doc["formation"] = lis[1]
    doc["date"] = lis[2]
    doc["id"] = lis[3]
    doc["lattes_id"] = doc["id"]
    return doc

groups = []
path = sys.argv[1]
print(path)

for i in range(1, 20):
    i+=498
    group = path +'1/{}.html'.format(i)
    soup = open_and_load(group)
    parsed = parse(soup)
    parsed["people"] = []
    print_json(parsed)
    groups.append(parsed)




df = pd.DataFrame(groups)
print(df)
print(path)

people = pd.read_csv(path +'/1/researcher_groups.csv', header=None, names=["name","grad","date","to_drop","id_people","id"])
people = people.dropna()
people["id"] = people["id"].transform(lambda x: x.split("/")[-1]) 
people = people.groupby('id')[["name", "grad", "date", "id_people"]].apply(lambda x: x.values.tolist()).to_frame()
people = people.reset_index()
people.columns = ["id", "peop"]
people["peop"] = list(map(lambda x: [list_to_json(i) for i in x], people["peop"]))
df = df.merge(people, on="id")
df["people"] = df["peop"]
df = df.drop(columns=['peop'])
jsons = json.loads(df.to_json(orient='records'))

for doc in jsons:
    print_json(doc)
# print(jsons[0])

