import requests
import csv
from bs4 import BeautifulSoup
from samshoparser import CharacterWebpageInfo, SamShoDataParser
from samshodatabase import SamShoDatabase

def getCharacters():
    with open('chars.csv', mode='r') as charCsv:
        csvReader = csv.reader(charCsv)
        chars = [CharacterWebpageInfo(row[0], row[1]) for row in csvReader]
    return chars

dbPath = "" # TODO: read this as input
chars = getCharacters()
dataParser = SamShoDataParser(chars)

moves = [move.toTuple() for move in dataParser.getDataForAllChars()]

database = SamShoDatabase(dbPath)

dbConn = database.connect()
database.insertIntoMoveTable(dbConn, moves)
database.disconnect(dbConn)

print("done!")