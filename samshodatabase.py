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
            cursor.executemany(insertQuery, moves)
        except sqlite3.Error as sqlErr:
            conn.rollback()
        conn.commit()

    def disconnect(self, conn: sqlite3.Connection):
        conn.close()

    def _buildInsertQuery(self):
        """Generate the insert statement for populating the Moves table"""
        # For posterity: https://stackoverflow.com/a/13378570
        sql = []
        sql.append(f"insert into {self.moveTableName} (")
        sql.append(", ".join(self.columns))
        sql.append(") values (")
        sql.append(", ".join(["?" for x in self.columns]))
        sql.append(")")

        return "".join(sql)