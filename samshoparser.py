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
    def __init__(self, charId, name, dmg, startup, active, total, cancelStart, cancelEnd, clashStart, clashEnd, onHit, backHit, onBlock, knockdown, guard, notes, lateCancelStart = None, lateCancelEnd = None):
        self.characterId = charId
        self.name = name
        self.damage = dmg
        self.startupFrames = startup
        self.activeFrames = active
        self.totalFrames = total
        self.cancelWindowStart = cancelStart
        self.cancelWindowEnd = cancelEnd
        self.lateCancelWindowStart = lateCancelStart
        self.lateCancelWindowEnd = lateCancelEnd
        self.weaponClashStart = clashStart
        self.weaponClashEnd = clashEnd
        self.advantageOnHit = onHit
        self.advantageOnBackhit = backHit
        self.advantageOnBlock = onBlock
        self.advantageKnockdown = knockdown
        self.guardLevel = guard
        self.notes = notes

class TableParser(object):
    def __init__(self, dataRows, char):
        self.tableRows = dataRows
        self.character = char

    def extractMovesFromTable(self):
        for moveRow in self.tableRows:
            moveData = moveRow.find_all("td")

    def _formatRowData(self, data):
        formattedData = {}
        formattedData["MoveCancelData"] = self._formatMoveCancelData(data[5].text)
        formattedData["MoveClashData"] = self._formatWeaponClashData(data[6].text)
        formattedData["OnHitData"] = self._formatAdvantageData(data[7].text)
        formattedData["OnBackhitData"] = self._formatAdvantageData(data[8].text)
        formattedData["OnBlockData"] = self._formatAdvantageData(data[9].text)
        formattedData["Guard"] = self._formatGuardLevelData(data[10].text)
        return formattedData

    def _formatMoveCancelData(self, cancelData: str):
        rowDataFormatter = RowDataFormatter()
        moveCancelData = { }
        if cancelData == "x":
            return None
        else:
            if "/" in cancelData:
                splitCancelData = cancelData.split("/")
                earlyCancelRange = rowDataFormatter.splitFrameRangeMoveData(splitCancelData[0])
                lateCancelRange = rowDataFormatter.splitFrameRangeMoveData(splitCancelData[1])
                moveCancelData["EarlyCancelStart"] = int(earlyCancelRange[0])
                moveCancelData["EarlyCancelEnd"] = int(earlyCancelRange[1])
                moveCancelData["LateCancelStart"] = int(lateCancelRange[0])
                moveCancelData["LateCancelEnd"] = int(lateCancelRange[1])
            elif "end" in cancelData:
                # Enja has a 3-special setup, where the second special can cancel into the third
                # from frame 13 all the way until the opponent hits the wall and bounces back
                # towards Enja. This is the only move in the game like this (and is consequently)
                # the hardest move to land in SamSho 5 Special! The cancel end value will be represented
                # by 999 until I look into this more
                splitEnjaSpecial = rowDataFormatter.splitFrameRangeMoveData(cancelData)
                moveCancelData["EarlyCancelStart"] = int(splitEnjaSpecial[0])
                moveCancelData["EarlyCancelEnd"] = 999
            else:
                cancelRange = rowDataFormatter.splitFrameRangeMoveData(cancelData)
                moveCancelData["EarlyCancelStart"] = int(cancelRange[0])
                moveCancelData["EarlyCancelEnd"] = int(cancelRange[1])
        return moveCancelData

    def _formatWeaponClashData(self, weaponClashData: str):
        rowDataFormatter = RowDataFormatter()
        if "~" in weaponClashData:
            weaponClashRange = rowDataFormatter.splitFrameRangeMoveData(weaponClashData)
            return {
                "WeaponClashStart": int(weaponClashRange[0]),
                "WeaponClashEnd": int(weaponClashRange[1])
            }
        else:
            return int(rowDataFormatter.extractSingleFrameWeaponClashData(weaponClashData))

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
        for currentChar in self.characters:
            dataTable = self._getFrameDataTableForCharacter(currentChar)
            tableParser = TableParser(dataTable, currentChar)

    def _getFrameDataTableForCharacter(self, character: CharacterWebpageInfo):
        pageUrl = f"{self.wikiUrl}{character.characterPageUrlName}"
        pageData = requests.get(pageUrl)
        pageObject = BeautifulSoup(pageData.text, 'lxml')
        frameDataTable = pageObject.find("div", class_="mw-parser-output").find("table", {"cellspacing":"0"}).find_all("tr")
        frameDataTable.pop(0)
        return frameDataTable