import requests
from bs4 import BeautifulSoup
from dataformat import RowDataFormatter

class CharacterWebpageInfo(object):
    def __init__(self, id, pageUrl):
        self.characterId = id
        self.characterPageUrlName = pageUrl

class SamShoMove(object):
    """
    A DTO for a Samurai Shodown move's frame data
    """
    def __init__(self, charId, moveData: dict):
        self.characterId = charId
        self.name = moveData["Name"]
        self.damage = moveData["Damage"]
        self.startupFrames = moveData["Startup"]
        self.activeFrames = moveData["ActiveFrames"]
        self.totalFrames = moveData["TotalFrames"]
        self.cancelWindows = moveData["Cancel"]
        self.weaponClashWindows = moveData["Clash"]
        self.advantageOnHit = moveData["OnHit"]
        self.advantageOnBackhit = moveData["OnBackhit"]
        self.advantageOnBlock = moveData["OnBlock"]
        self.advantageKnockdown = self._assignKnockdown(moveData["OnHit"], moveData["OnBackhit"])
        self.guardLevel = moveData["Guard"]
        self.notes = moveData["Notes"]

    def _assignKnockdown(self, onHit, onBackhit):
        if onHit is None and onBackhit is None:
            return True
        else:
            return False

class TableParser(object):
    def __init__(self, dataRows, charId):
        self.tableRows = dataRows
        self.characterId = charId

    def extractMovesFromTable(self):
        extractedMoves = []
        for moveRow in self.tableRows:
            finalData = {}
            moveData = moveRow.find_all("td")            
            finalData["Name"] = moveData[0].text
            finalData["Damage"] = moveData[1].text
            finalData["Startup"] = moveData[2].text
            finalData["ActiveFrames"] = moveData[3].text
            finalData["TotalFrames"] = moveData[4].text
            finalData["Cancel"] = self._formatMoveCancelData(moveData[5].text)
            finalData["Clash"] = self._formatWeaponClashData(moveData[6].text)
            finalData["OnHit"] = self._formatAdvantageData(moveData[7].text)
            finalData["OnBackhit"] = self._formatAdvantageData(moveData[8].text)
            finalData["OnBlock"] = self._formatAdvantageData(moveData[9].text)
            finalData["Guard"] = self._formatGuardLevelData(moveData[10].text)
            finalData["Notes"] = moveData[11].text

            move = SamShoMove(self.characterId, finalData)
            extractedMoves.append(move)
        return extractedMoves

    def _formatMoveCancelData(self, cancelData: str):
        rowDataFormatter = RowDataFormatter()
        moveCancelData: list = []
        if cancelData == "x":
            return None
        else:
            if "/" in cancelData:
                splitCancelData = cancelData.split("/")
                earlyCancelRange = rowDataFormatter.splitFrameRangeMoveData(splitCancelData[0])
                lateCancelRange = rowDataFormatter.splitFrameRangeMoveData(splitCancelData[1])
                moveCancelData.append([int(x) for x in earlyCancelRange])
                moveCancelData.append([int(x) for x in lateCancelRange])
            elif "end" in cancelData:
                # Enja has a 3-special setup, where the second special can cancel into the third
                # from frame 13 all the way until the opponent hits the wall and bounces back
                # towards Enja. This is the only move in the game like this (and is consequently)
                # the hardest move to land in SamSho 5 Special! The cancel end value will be represented
                # by 999 until I look into this more
                splitEnjaSpecial = rowDataFormatter.splitFrameRangeMoveData(cancelData)
                moveCancelData.append([int(splitEnjaSpecial[0]), 999])
            else:
                cancelRange = rowDataFormatter.splitFrameRangeMoveData(cancelData)
                moveCancelData.append(int(cancelRange))
        return moveCancelData

    def _formatWeaponClashData(self, weaponClashData: str):
        rowDataFormatter = RowDataFormatter()
        weaponClashStorage: list = []
        if "/" in weaponClashData:
            splitClashData = weaponClashData.split("/")
            earlyWeaponClash = rowDataFormatter.splitFrameRangeMoveData(splitClashData[0])
            lateWeaponClash = rowDataFormatter.splitFrameRangeMoveData(splitClashData[1])
            weaponClashStorage.append([int(x) for x in earlyWeaponClash])
            weaponClashStorage.append([int(x) for x in lateWeaponClash])
            return weaponClashStorage
        if "~" in weaponClashData:
            weaponClashRange = rowDataFormatter.splitFrameRangeMoveData(weaponClashData)
            weaponClashStorage.append([int(x) for x in weaponClashRange])
            return weaponClashStorage
        else:
            weaponClashFrame = rowDataFormatter.extractSingleFrameWeaponClashData(weaponClashData)
            weaponClashStorage.append(int(weaponClashFrame))
            return weaponClashStorage

    def _formatAdvantageData(self, advData: str):
        if advData.lower() == "kd":
            return None
        else:
            try:
                return int(advData)
            except ValueError as valErr:
                return None

    def _formatGuardLevelData(self, guardData: str):
        if guardData.lower() == "low":
            return 0
        elif guardData.lower() == "mid":
            return 1
        else:
            return 2

class SamShoDataParser(object):
    def __init__(self, characters):
        self.wikiUrl = "https://wiki.gbl.gg/w/Samurai_Shodown_V_Special/"
        self.characters = characters

    def getDataForAllChars(self):
        dataForChars: list = []
        for currentChar in self.characters:
            dataTable = self._getFrameDataTableForCharacter(currentChar)
            tableParser = TableParser(dataTable, currentChar.characterId)
            currentCharMoves = tableParser.extractMovesFromTable()
            dataForChars.extend(currentCharMoves)
        return dataForChars

    def _getFrameDataTableForCharacter(self, character: CharacterWebpageInfo):
        pageUrl = f"{self.wikiUrl}{character.characterPageUrlName}"
        pageData = requests.get(pageUrl)
        pageObject = BeautifulSoup(pageData.text, 'lxml')
        tables = pageObject.find("div", class_="mw-parser-output").find_all("table", {"cellspacing":"0"})
        
        if len(tables) == 1:
            frameDataTable = tables[0].find_all("tr")
            frameDataTable.pop(0)
            return frameDataTable
        else:
            frameDataTable = tables[1].find_all("tr")
            frameDataTable.pop(0)
            return frameDataTable