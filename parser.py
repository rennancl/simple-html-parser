import json
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
    return parsed

for i in range(1, 500):
    print(i)
    group = './0/{}.html'.format(i)
    soup = open_and_load(group)
    parsed = parse(soup)
    print_json(parsed)
    break

# soup = open_and_load('./0/400.html')
# parsed = parse(soup)
# print_json(parsed)

