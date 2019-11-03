import re, csv, os, glob
from bs4 import BeautifulSoup
from time import sleep, time
from random import uniform, randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException    

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument('window-size=1920x1080')
driver = webdriver.Chrome("/home/rennancordeiro/Documents/latin/chromedriver_linux64/chromedriver", chrome_options=options)

urls = []
for dir in range(78):
    for filename in glob.glob("/home/rennancordeiro/Documents/latin/" + str(dir) + "/*"):
        print(filename)
        filename = "/home/rennancordeiro/Documents/latin/0/0.html"
        records = []
        seen = []
        with open(filename, 'r') as page:
            html = page.read().replace('\n', '')
        soup = BeautifulSoup(html, "html.parser")
        divs = soup.find_all('div', attrs={'style': 'text-align: center !important;'})
        try:
            url = str(divs[0])[80:125]
            print(url)
        except:
            continue
        urls.append(url) 
        driver.get("http://www." + url)
        
        for i in range(10):
            print(i)
            sleep(1)

        for j in [2, 3]:
            table = soup.find_all("table")[j]
            table = [[td.text for td in row.find_all("td")] for row in table.select("tr")]
            table.pop(0)
            print(table)            
            for i in range(len(table)):
                record = table[i]
                command = "mojarra.jsfcljs(document.getElementById('idFormVisualizarGrupoPesquisa'),{'idFormVisualizarGrupoPesquisa:j_idt261:"+str(i)+":idBtnVisualizarEspelhoPesquisador':'idFormVisualizarGrupoPesquisa:j_idt261:" +str(i)+ ":idBtnVisualizarEspelhoPesquisador'},'_blank');"
                driver.execute_script(command)
                driver.switch_to.window(driver.window_handles[1])
                content = driver.page_source
                soup_researcher = BeautifulSoup(content, "html.parser")
                divs_researcher = soup_researcher.find_all('div', attrs={'style': 'text-align: center !important;'})
                try:
                    researcher = str(divs_researcher[0])[80:126].split("/")[-1]
                except:
                    continue
                if researcher not in seen:
                    seen.append(researcher)
                    with open("./" + str(dir) + "/p_"+ researcher +  ".html", "w") as text_file:
                        text_file.write(content)
                    record.append(content)
                    record.append(url)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    records.append(record)
                    print("Sucess")
        break

    break
print(len(urls))
# url = "http://dgp.cnpq.br/dgp/faces/consulta/consulta_parametrizada.jsf"
# driver.get(url)

# sleep(10)


# count = 0
# folder = 0
# if not os.path.exists("./" + str(folder)):
#     os.mkdir("./" + str(folder))
# for i in range(39592):
#     count+= 1

#     print(i+25)
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     if((i+25) % 25 == 0):
#         print(i+25)

#         click_command = 'document.getElementsByClassName("ui-paginator-next ui-state-default ui-corner-all")[0].click()'
#         driver.execute_script(click_command)
#         # next_page = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "ui-paginator-next ui-state-default ui-corner-all")))
#         # next_page = driver.find_element_by_xpath("//span[@class='ui-paginator-next ui-state-default ui-corner-all']")
#         # next_page = driver.find_element_by_class_name("ui-paginator-next ui-state-default ui-corner-all")
#         # next_page.click()
#         sleep(10)


#     if count >= 500:
#         count = 0
#         folder+= 1
#         if not os.path.exists("./" + str(folder)):
#             os.mkdir("./" + str(folder))

#     element = "idFormConsultaParametrizada:resultadoDataList:"+ str(i+25)+ ":idBtnVisualizarEspelhoGrupo"
#     page =  WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, element)))
#     # page.click()
#     # driver.find_element_by_id("idFormConsultaParametrizada:resultadoDataList:"+ str(i+25)+ ":idBtnVisualizarEspelhoGrupo").click()

#     command = "mojarra.jsfcljs(document.getElementById('idFormConsultaParametrizada'),{'idFormConsultaParametrizada:resultadoDataList:" + str(i+25) + ":idBtnVisualizarEspelhoGrupo':'idFormConsultaParametrizada:resultadoDataList:" + str(i+25) + ":idBtnVisualizarEspelhoGrupo'},'_blank');"
#     driver.execute_script(command)
#     driver.switch_to.window(driver.window_handles[1])

#     for _ in range(60):        
#         try:
#             driver.find_element_by_xpath("//div[@id='recursosHumanos']")
#             break
#         except:        
#             print("not yet")
#             sleep(1)

#     content = driver.page_source
#     with open("./" + str(folder) + "/" + str(i) + ".html", "w") as text_file:
#         text_file.write(content)
#     driver.close()
#     driver.switch_to.window(driver.window_handles[0])

