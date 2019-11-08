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

groups = []
path = sys.argv[1]

print(path)

for i in range(1, 20):
    group = path +'/0/{}.html'.format(i)
    soup = open_and_load(group)
    parsed = parse(soup)
    print_json(parsed)
    groups.append(parsed)

# df = pd.DataFrame(groups)
# print(df)