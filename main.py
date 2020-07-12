import requests
from bs4 import BeautifulSoup

class SamShoMove(object):
    """
    A DTO for a Samurai Shodown move's frame data
    """
    def __init__(self, charId, name, dmg, startup, active, total, cancelStart, cancelEnd, clashStart, clashEnd, onHit, backHit, onBlock, guard, notes):
        self.characterId = charId
        self.name = name
        self.damage = dmg
        self.startupFrames = startup
        self.activeFrames = active
        self.totalFrames = total
        self.cancelWindowStart = cancelStart
        self.cancelWindowEnd = cancelEnd
        self.weaponClashStart = clashStart
        self.weaponClashEnd = clashEnd
        self.advantageOnHit = onHit
        self.advantageOnBackhit = backHit
        self.advantageOnBlock = onBlock
        self.guardLevel = guard
        self.notes = notes

rimuPage = "https://wiki.gbl.gg/w/Samurai_Shodown_V_Special/Rimururu"
pageData = requests.get(rimuPage)
pageObject = BeautifulSoup(pageData.text, 'lxml')

frameDataTable = pageObject.find("div", class_="mw-parser-output").find("table", {"cellspacing": "0"}).find_all("tr")



print("done!")