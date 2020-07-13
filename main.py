import requests
import csv
from bs4 import BeautifulSoup
from samshoparser import CharacterWebpageInfo, SamShoDataParser

def getCharacters():
    with open('chars.csv', mode='r') as charCsv:
        csvReader = csv.reader(charCsv)
        chars = [CharacterWebpageInfo(row[0], row[1]) for row in csvReader]
    return chars

chars = getCharacters()
dataParser = SamShoDataParser(chars)

moves = dataParser.getDataForAllChars()

print("done!")