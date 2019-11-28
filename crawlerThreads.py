import re, csv, os, glob
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep, time
from random import uniform, randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException    
from threading import Thread
from logging import info

def get_url_by_html(filename):
    with open(filename, 'r') as page:
        html = page.read().replace('\n', '')
    soup = BeautifulSoup(html, "html.parser")
    divs = soup.find_all('div', attrs={'style': 'text-align: center !important;'})
    try:
        url = str(divs[0])[80:125]
        return soup, url
    except:
        return soup, ""

def wait_seconds(seconds):
    for i in range(seconds):
        print(i+1)
        sleep(1)
    return

def get_researchers_table(soup, j):
    table = soup.find_all("table")[j]
    table = [[td.text for td in row.find_all("td")] for row in table.select("tr")]
    table.pop(0)
    return table

def get_div_researcher(i, driver):
    command = "mojarra.jsfcljs(document.getElementById('idFormVisualizarGrupoPesquisa'),{'idFormVisualizarGrupoPesquisa:j_idt261:"+str(i)+":idBtnVisualizarEspelhoPesquisador':'idFormVisualizarGrupoPesquisa:j_idt261:" +str(i)+ ":idBtnVisualizarEspelhoPesquisador'},'_blank');"
    driver.execute_script(command)
    driver.switch_to.window(driver.window_handles[1])
    content = driver.page_source
    soup_researcher = BeautifulSoup(content, "html.parser")
    divs_researcher = soup_researcher.find_all('div', attrs={'style': 'text-align: center !important;'})
    return divs_researcher, content

def get_researchers_url(divs_researcher):
    return str(divs_researcher[0])[80:126].split("/")[-1]

def craw_function(dir):
    records = []
    seen = []       
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Chrome("/home/rennancordeiro/Documents/latin/chromedriver_linux64/chromedriver", chrome_options=options)
    for filename in glob.glob("./" + str(dir) + "/*"):
        if 'p' in filename:
            continue
        soup, url = get_url_by_html(filename)
        if not url:
            # in case of couldn't find url in page, goes to next page
            continue
        # acess the page to download groups
        driver.get("http://www." + url)
        # wait till page can be on
        # wait_seconds(1)

        for j in [2, 3]:
            researchers = get_researchers_table(soup, j)
            for i, record in enumerate(researchers):
                try:
                    divs_researcher, content = get_div_researcher(i, driver)
                    researcher = get_researchers_url(divs_researcher)
                except:
                    continue

                record.append(researcher)
                record.append(url)
                records.append(record)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                if researcher not in seen:
                    seen.append(researcher)
                    with open("./" + str(dir) + "/p_"+ researcher +  ".html", "w") as text_file:
                        text_file.write(content)

    df = pd.DataFrame(records)
    df.to_csv("./" + str(dir) + "/researcher_groups.csv")

def craw_threads():
    threads = list()
    threads_log = open("threads_log.txt", "a")
    
    for dir in [51, 52, 53 , 54, 55, 56, 57 , 58, 59 , 60, 61, 62, 63, 64, 65]:
        t = Thread(target=craw_function,args=(dir,))
        threads.append(t)
        t.start()
        print("Main: thread for ", dir, "started")
        
    for index, thread in enumerate(threads):
        threads_log.write("Main: before joining thread:\n" + str(index))
        print("Main: before joining thread %d.", index)
        
        thread.join()
        
        threads_log.write("Main: thread done:\n" + str(index))
        print("Main: thread %d done", index)

craw_threads()
