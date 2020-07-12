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
        moveCancelData = self._formatMoveCancelData(data[5].text)
        moveClashData = self._formatWeaponClashData(data[6].text)

    def _formatMoveCancelData(self, cancelData):
        moveCancelData = {
            "EarlyCancelStart": None,
            "EarlyCancelEnd": None,
            "LateCancelStart": None,
            "LateCancelEnd": None
        }
        if cancelData == "x":
            return moveCancelData
        else:
            if "/" in cancelData:
                splitCancelData = cancelData.split("/")
                earlyCancelRange = RowDataFormatter.splitFrameRangeMoveData(splitCancelData[0])
                lateCancelRange = RowDataFormatter.splitFrameRangeMoveData(splitCancelData[1])
                moveCancelData["EarlyCancelStart"] = int(earlyCancelRange[0])
                moveCancelData["EarlyCancelEnd"] = int(earlyCancelRange[1])
                moveCancelData["LateCancelStart"] = int(lateCancelRange[0])
                moveCancelData["LateCancelEnd"] = int(lateCancelRange[1])
            else:
                cancelRange = RowDataFormatter.splitFrameRangeMoveData(cancelData)
                moveCancelData["EarlyCancelStart"] = int(cancelRange[0])
                moveCancelData["EarlyCancelEnd"] = int(cancelRange[1])
        return moveCancelData

    def _formatWeaponClashData(self, weaponClashData):
        if "~" in weaponClashData:
            weaponClashRange = RowDataFormatter.splitFrameRangeMoveData(weaponClashData)
            return {
                "WeaponClashStart": int(weaponClashRange[0]),
                "WeaponClashEnd": int(weaponClashRange[1])
            }
        else:
            return int(RowDataFormatter.extractSingleFrameWeaponClashData(weaponClashData))

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