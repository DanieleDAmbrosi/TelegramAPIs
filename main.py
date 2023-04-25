from dotenv import dotenv_values
import sqlite3

conn = sqlite3.connect("./data/data.db")
cursor = conn.cursor()

global __env
__env = dotenv_values(".env")
token = __env.get("SECRET_TOKEN")

from telegram import bot

mybot = bot(token)

print(mybot.link())

sqlite_select_Query = "select sqlite_version();"
cursor.execute(sqlite_select_Query)
record = cursor.fetchall()
print("SQLite Database Version is: ", record)