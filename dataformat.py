import re

class RowDataFormatter(object):
    def __init__(self):
        super().__init__()

    def parseSingularFrameAsInteger(self, frameData: str):
        """If the cancel or weapon clash is only possible on a single frame,
        determine if there is a parenthesis counting that one frame, and
        return just the frame value as an integer.
        """
        parsedFrameData = []
        data = None
        if "(" in frameData:
            data = self._extractSingleFrameDataAsInteger(frameData)
        else:
            if frameData.isalpha():
            # There's an edge case floating around where there's just
            # a "Y" as some single piece of data. I haven't figured
            # out what this "Y" means so just return null for now
                data = None
        parsedFrameData.append(data)
        parsedFrameData.extend([None, None, None])
        return parsedFrameData

    def splitFrameRangeMoveDataAsListOfInt(self, cancelData: str):
        """Takes a range of frames separated by either a ~ or -
        and extracts the numbers that signal the start of the
        window and the end of the window, converting both of
        those values to integers.
        """
        frameRange = cancelData[0:cancelData.find("(")]
        if "~" in frameRange:
            return [int(x) for x in frameRange.split("~")]
        elif "-" in frameRange:
            return [int(x) for x in frameRange.split("-")]

    def splitEnjaRikudouRekka(self, rikudouRekka: str):
        """This is a special version of splitFrameRangeMoveDataAsListOfInt
        for Enja. In SamSho 5 Special, Enja has a 3-special setup, where 
        his second special can cancel into the third from frame 13 all the
        way until the opponent hits the wall and bounces back towards Enja. 
        This is the only move in the game like this (and is consequently
        the hardest move to land in SamSho 5 Special!); the cancel end
        value will be represented by 999 until I look into this more.
        """
        parsedRekkaString = rikudouRekka[0:rikudouRekka.find("(")]
        rekkaParts, parsedRekkaFrameData = [], []
        if "~" in parsedRekkaString:
            rekkaParts = parsedRekkaString.split("~")
        elif "-" in parsedRekkaString:
            rekkaParts = parsedRekkaString.split("-")
        rekkaParts[1] = "999"

        for part in rekkaParts:
            parsedRekkaFrameData.append(int(part))
        
        parsedRekkaFrameData.extend([None, None])
        return parsedRekkaFrameData

    def splitGroupedFrameDataAndReturnAsList(self, groupedFrames: str):
        """Splits frame data grouped by / (backslash), parses each section,
        and returns the pieces as a list
        """
        splitResults: list = []
        splitData = groupedFrames.split("/")

        def formatFrameDataAccordingToCase(data):
            """Calls the appropriate format method based on the
            indicators in the data.
            """
            if "~" in data or "-" in data:
                return self.splitFrameRangeMoveDataAsListOfInt(data)
            else:
                return self.parseSingularFrameAsInteger(data)

        firstData = formatFrameDataAccordingToCase(splitData[0])
        secondData = formatFrameDataAccordingToCase(splitData[1])

        if isinstance(firstData, int):
            splitResults.append(firstData)
        else:
            splitResults.extend(firstData)

        if isinstance(secondData, int):
            splitResults.append(secondData)
        else:
            splitResults.extend(secondData)
        return splitResults

    def convertStringValueForPurelyIntegerData(self, basicData: str):
        """Converts the string values for purely integer-based data
        like move damage, active frames, etc. If the move doesn't deal
        damage or have active frames (i.e., a command grab), this will
        return null
        """
        if basicData.isnumeric():
            return int(basicData)
        else:
            return None

    def _extractSingleFrameDataAsInteger(self, data: str):
        """Trims the singular frame such that the parenthesis containing
        '(1)' is not present and casts the frame to an integer before
        returning it to the caller.
        """
        return int(data[0:data.find("(")])