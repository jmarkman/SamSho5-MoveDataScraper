import requests
import csv
import sys
from bs4 import BeautifulSoup
from os import path
from samshoparser import CharacterWebpageInfo, SamShoDataParser
from samshodatabase import SamShoDatabase

def getCharacters():
    with open('chars.csv', mode='r') as charCsv:
        csvReader = csv.reader(charCsv)
        chars = [CharacterWebpageInfo(row[0], row[1]) for row in csvReader]
    return chars

def getDatabaseFilePath():
    if len(sys.argv) == 0:
        print("No filepath input was provided!")
        sys.exit(2)
    elif len(sys.argv) > 1:
        print("Too many parameters were provided! The only parameter needed is a path to the sqlite database.")
        sys.exit(2)
    else:
        if not path.exists(sys.argv[0]):
            print(f"The path '{sys.argv[0]}' was not valid. Check the path and try again.")
            sys.exit(1)
        else:
            return sys.argv[0]

def getMovesFromWiki(characters: list):
    dataParser = SamShoDataParser(characters)
    return [move.toTuple() for move in dataParser.getDataForAllChars()]

def addMovesToDatabase(moves: list, dbPath: str):
    database = SamShoDatabase(dbPath)
    dbConn = database.connect()
    database.insertIntoMoveTable(dbConn, moves)
    database.disconnect(dbConn)

if __name__ == "__main__":
    dbPath = getDatabaseFilePath()
    chars = getCharacters()
    moves = getMovesFromWiki(chars)
    addMovesToDatabase(moves, dbPath)
    print(f"Done! Added {len(moves)} moves to the sqlite database at '{dbPath}'")