from bs4 import BeautifulSoup


with open('/home/rennancordeiro/Documents/latin/78/39035.html', 'r') as f:
    htmltxt = f.read().replace('\n', '')


soup = BeautifulSoup(htmltxt, 'lxml')
att = soup.findAll("div", {"class": "control-group"})
# print(dir(att[19]))

page = {}
for at in att:
    try:
        page[at.contents[0].contents[0]] = at.contents[2].contents[0]
        # print(at.contents[0].contents[0])
        # print(at.contents[2].contents[0])
    except:
        pass
        continue


