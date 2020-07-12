import requests
import csv
from bs4 import BeautifulSoup
from samshoparser import *

def getCharacters():
    with open('chars.csv', mode='r') as charCsv:
        csvReader = csv.reader(charCsv)
        chars = [CharacterWebpageInfo(row[0], row[1]) for row in csvReader]
    return chars

chars = getCharacters()
dataParser = SamShoDataParser(chars)

rimuPage = "https://wiki.gbl.gg/w/Samurai_Shodown_V_Special/Rimururu"
pageData = requests.get(rimuPage)
pageObject = BeautifulSoup(pageData.text, 'lxml')

frameDataTable = pageObject.find("div", class_="mw-parser-output").find("table", {"cellspacing": "0"}).find_all("tr")



print("done!")