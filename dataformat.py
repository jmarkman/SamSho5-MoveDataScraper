import re

class RowDataFormatter(object):
    def __init__(self):
        super().__init__()

    def splitFrameRangeMoveData(self, cancelData: str):
        return cancelData[0:cancelData.find("(")].split("~")

    def extractSingleFrameWeaponClashData(self, clashData: str):
        return clashData[0:clashData.find("(")]