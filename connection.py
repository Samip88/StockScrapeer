import sqlite3

conn = sqlite3.connect('stocktrade.db')

cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS rawstock (symbol TEXT, ltp REAL, change REAL, open REAL, high REAL, low REAL, volume REAL, close REAL, change_percent REAL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Stock (symbol TEXT, ltp REAL, change REAL, open REAL, high REAL, low REAL, volume REAL, close REAL, change_percent REAL, last_updated DATETIME)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS update_log (last_updated DATETIME)''')

conn.commit()

conn.commit()

conn.commit()


conn.close()