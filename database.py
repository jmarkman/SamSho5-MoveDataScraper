import sqlite3
from samshoparser import SamShoMove

class SamShoDatabase(object):
    def __init__(self, dbPath):
        self.databasePath = dbPath
        self.moveTableName = "Moves"
        self.columns = [
            "CharacterId",
            "Name",
            "Damage",
            "StartupFrames",
            "ActiveFrames",
            "TotalFrames",
            "CancelWindowStart",
            "CancelWindowEnd",
            "LateCancelWindowStart",
            "LateCancelWindowEnd",
            "WeaponClashStart",
            "WeaponClashEnd",
            "LateWeaponClashStart",
            "LateWeaponClashEnd",
            "OnHit",
            "OnBackhit",
            "OnBlock",
            "CausesKnockdown",
            "GuardStance",
            "Notes"
        ]

    def connect(self):
        return sqlite3.connect(self.databasePath)

    def insertIntoMoveTable(self, conn: sqlite3.Connection, moves: list):
        cursor = conn.cursor()
        insertQuery = self._buildInsertQuery()
        try:
            for move in moves:
                cursor.execute(insertQuery, )
        except sqlite3.Error as sqlErr:
            conn.rollback()

    def _buildInsertQuery(self):
        query = f"insert into {self.moveTableName}"
        colIdx = 0
        while colIdx < len(self.columns):
            if colIdx == 0:
                query += f"({self.columns[colIdx]}, "
                colIdx += 1
            elif colIdx == len(colIdx) - 1:
                query += f"{self.columns[colIdx]})"
                colIdx += 1
            else:
                query += f"{self.columns[colIdx], }"
                colIdx += 1

        query += " values "

        questionMarkIdx = 0
        while questionMarkIdx < len(self.columns):
            if questionMarkIdx == 0:
                query += "(?,"
                questionMarkIdx += 1
            elif questionMarkIdx == len(colIdx) - 1:
                query += "?)"
                questionMarkIdx += 1
            else:
                query += "?"
                questionMarkIdx += 1
        
        return query