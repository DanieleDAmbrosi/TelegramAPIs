import sqlite3, json
from typing import Any
import array as arr
class SingletonMeta(type):
    _instances = {}

    def __call__(self, *args: Any, **kwds: Any):
        if self not in self._instances:
            instance = super().__call__(*args, **kwds)
            self._instances[self] = instance
        return self._instances[self]

class Database(metaclass=SingletonMeta):
    _connection = None
    _db_path = ""

    def __init__(self, db_path):
        self._db_path = db_path
        pass

    def connect(self) -> sqlite3.Connection:
        if self._connection == None:
            self._connection = sqlite3.connect(self._db_path)
        return self._connection
    
    def close(self):
        self._connection.close()
        self._connection = None
        pass

class DatabaseHandler():
    _db: Database
    _model: dict = {}

    def __init__(self, db: Database, tables: arr):
        self.connect(db, tables)
        pass

    def connect(self, db: Database, tables: arr):
        self._db = db
        conn = self._db.connect()
        curs = conn.cursor()
        for table in tables:
            curs.execute(f"PRAGMA table_info({table})")
            raw_cols = curs.fetchall()
            cols = [col[1] for col in raw_cols]
            self._model.update({table: cols})
        curs.close()
        pass

    def insert(self, table: str, values: tuple):
        conn = self._db.connect()
        curs = conn.cursor()
        cols = self._model.get(table)
        if cols != None:
            comma = ","
            if len(cols) == len(values):
                dummy = list(values)
                for i in range(len(values)):
                    if type(values[i]) == str and str(values[i]) != "Null":
                        dummy[i] = str(values[i]).replace("'", "")
                        dummy[i] = f"'{dummy[i]}'"
                values = tuple(dummy)
                query = f"INSERT INTO {table}({comma.join(cols)}) VALUES({comma.join(map(str, values))})"
                curs.execute(query)
        else:
            raise Exception("The table does not exist")
        conn.commit()
        curs.close()
        pass

    def select(self, table: str, fields: arr = []):
        conn = self._db.connect()
        curs = conn.cursor()
        if self._model.get(table) == None:
            raise Exception("The table does not exist")
        if fields == None or len(fields) == 0:
            cols = "*"
        elif all([field in self._model.get(table) for field in fields]):
            cols = ",".join(fields)
        else:
            raise Exception("The colomn does not exist")
        result = curs.execute(f"SELECT {cols} FROM {table}").fetchall()
        curs.close()
        return result

    def close(self):
        self._db.close()
        self._db = None
        self._model = {}
        pass

    def delete_all(self, tables: arr = []):
        conn = self._db.connect()
        curs = conn.cursor()

        if all([table in self._model.keys() for table in tables]):
            for table in tables:
                curs.execute(f"DELETE FROM {table}")
        else:
            raise Exception("The table does not exist")

        conn.commit()
        curs.close()
        pass

    def getmodel(self) -> dict:
        return self._model