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
        """Given move cancel data as a string, will return a list of
        integer values representing on what frames a given move can be
        canceled into another
        """
        rowDataFormatter = RowDataFormatter()
        moveCancelData: list = []
        if cancelData == "x":
            # This means the move cannot be canceled according to the wiki
            return moveCancelData
        else:
            if "/" in cancelData:
                moveCancelData = rowDataFormatter.splitGroupedFrameDataAndReturnAsList(cancelData)
            elif "end" in cancelData:
                moveCancelData = rowDataFormatter.splitEnjaRikudouRekka(cancelData)
            else:
                moveCancelData = rowDataFormatter.splitFrameRangeMoveDataAsListOfInt(cancelData)
        return moveCancelData

    def _formatWeaponClashData(self, clashData: str):
        """Given weapon clash data as a string, will return a list of
        integer values representing on what frames a given move can
        clash with the opponent's move (i.e., when Haohmaru and Gaoh
        swing their weapons and the moves meet on screen at specific
        frames, they'll "clash" and the disarmament minigame will
        occur)
        """
        rowDataFormatter = RowDataFormatter()
        formattedClashData: list = []
        if "/" in clashData:
            formattedClashData = rowDataFormatter.splitGroupedFrameDataAndReturnAsList(clashData)
        elif "~" in clashData or "-" in clashData:
            formattedClashData = rowDataFormatter.splitFrameRangeMoveDataAsListOfInt(clashData)
        else:
            singleFrameClashData = rowDataFormatter.parseSingularFrameAsInteger(clashData)
            formattedClashData.append(singleFrameClashData)
        return formattedClashData

    def _formatAdvantageData(self, advData: str):
        """Given advantage data as a string, parse the integer value
        representing the plus/minus value of that move after an action.
        On moves that knock down the opponent on contact, this method
        will return None.
        """
        if advData.lower() == "kd":
            return None
        else:
            try:
                return int(advData)
            except ValueError as valErr:
                return None

    def _formatGuardLevelData(self, guardData: str):
        """Given guard data as a string, 'converts' that string
        to a corresponding integer value so it fits in the sqlite
        database
        """
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