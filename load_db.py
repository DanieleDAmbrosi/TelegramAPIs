import requests
from dotenv import dotenv_values

global sep, env_var
sep = ","
env_var = dotenv_values(".env")

# def build_insert(row: arr, ) -> str:
#     formatter = "'{value}' "
#     return f"UNION ALL SELECT {sep.join([formatter.format(value = v) for v in row])}"

# def build_query(data: list, map: arr, tableName: str) -> str:
#     query = ""
#     col_n = len(map)
#     formatter = "'{value}' AS '{col}' "
#     if col_n > 0:
#         query += f"INSERT INTO {tableName} SELECT {sep.join([formatter.format(value = v, col = c) for (v,c) in zip(data[0], map)])}"
#         for row in data[1:]:
#             query += build_insert(row)
#     return query

# def insert(data: list, map: arr, tableName: str, dbName: str = "data.db"):
#     db_path = dotenv_values(".env").get("DB_PATH")
#     conn = sqlite3.connect(db_path + dbName)
#     print(map)
#     print(data[0])
#     query = build_query(data, map, tableName)
#     #open("queryDump.txt", "a").write(query)
#     conn.execute(query, ())
#     conn.commit()
#     conn.close()
#     return
def reload_db():
    from database import Database, DatabaseHandler

    tables = ["impianti", "prezzi"]

    def download(resourceName: str):
        gov_endpoint = env_var.get("GOV_API")
        r = requests.get(gov_endpoint + resourceName)
        if r.status_code == 200:
            data = r.content.decode("utf-8").split("\n")
            import csv
            csv_data = csv.DictReader(data[1:], delimiter=";")
        return csv_data

    database = Database(env_var.get("DB_PATH") + env_var.get("DB_NAME"))
    dbHandler = DatabaseHandler(database, tables)

    dbHandler.delete_all(tables)

    data = download("anagrafica_impianti_attivi.csv")
    
    for d in list(data):
        if all([len(x.strip()) != 0 and x != "NULL" for x in map(str, d.values())]): #elimino tutti i record con valori nulli
            dbHandler.insert("impianti", tuple(d.values()))
    pass

    data = download("prezzo_alle_8.csv")
        
    for d in list(data):
        if all([len(x.strip()) != 0 and x != "NULL" for x in map(str, d.values())]): #elimino tutti i record con valori nulli
            dbHandler.insert("prezzi", tuple(["Null"]) + tuple(d.values()))
    pass

reload_db()