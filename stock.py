
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3








def convert_currency_string_to_float(currency_string):    
    return float(currency_string.replace(',', ''))


def get_last_updated_from_db():
    conn = sqlite3.connect("stocktrade.db")
    cursor = conn.cursor()
    cursor.execute("SELECT last_updated FROM update_log ORDER BY last_updated DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result
    




def create_last_updated(last_updated):
    conn = sqlite3.connect('stocktrade.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO update_log (last_updated) VALUES (?)", (last_updated,))
    conn.commit()
    conn.close()


def update_last_updated(last_updated):
    conn = sqlite3.connect('stocktrade.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE update_log SET last_updated = ?", (last_updated,))
    conn.commit()
    conn.close()

def data_append(data:list, new):
    ndata = []
    for i in data:
        n = i 
        n.append(new)
        ndata.append(n)
    return ndata 
def push_to_database(data, last_updated):
    try:
        # print([list(i.values()) for i in data])
        conn = sqlite3.connect('stocktrade.db')
        cursor = conn.cursor()
        data_formatted = [list(i.values()) for i in data]
        # data_formatted_with_ts =map(data_append,data_formatted,[last_updated for i in range(len(data_formatted))])
        data_formatted_with_ts =data_append(data_formatted,last_updated)

        cursor.executemany("INSERT INTO Stock(symbol, ltp, change, open, high, low, volume, close, change_percent,last_updated) VALUES (?,?,?,?,?,?,?,?,?,?)",data_formatted_with_ts)
        conn.commit()
        conn.close()
    except Exception as e:
        print("error here")
        print(e)
    


def sync_data():
    url = 'https://merolagani.com/LatestMarket.aspx'
    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(2)
    try:
        last_updated = driver.find_element(
            by=By.ID, value='live-trading-label-1').get_attribute('innerHTML')
        print(f"last updated : {last_updated}")
        if (last_updated == ''):
            print("Nothing")
            driver.close()
        else:
            # Parse this last_updated string `As of 2022/12/04 02:18:00` to get the date and time
            # and then insert it into the database

            print(last_updated)
            last_updated = last_updated.split(' ')[2:]
            # convert to datetime
            last_updated = ' '.join(last_updated)
            last_updated = datetime.strptime(last_updated, '%Y/%m/%d %H:%M:%S')
            last_updated_from_db = get_last_updated_from_db()
            if last_updated_from_db is None:
                create_last_updated(last_updated)
            elif last_updated_from_db == last_updated:
                print("Already updated")
                driver.close()
            else:
                table_ = driver.find_element(
                    By.XPATH, '/html/body/form/div[4]/div[8]/div[1]/div[4]/div/div[2]/table')

                tbody_ = table_.find_element(By.TAG_NAME, 'tbody')
                trs_ = tbody_.find_elements(By.TAG_NAME, 'tr')
                data = []
                for tr in trs_:
                    tds_ = tr.find_elements(By.TAG_NAME, 'td')
                    curr_data = {
                        "symbol": tds_[0].text,
                        "ltp": convert_currency_string_to_float(tds_[1].text),
                        "change": convert_currency_string_to_float(tds_[2].text),
                        "open": convert_currency_string_to_float(tds_[3].text),
                        "high": convert_currency_string_to_float(tds_[4].text),
                        "low": convert_currency_string_to_float(tds_[5].text),
                        "volume": convert_currency_string_to_float(tds_[6].text),
                        "close": convert_currency_string_to_float(tds_[7].text),
                        "change_percent": convert_currency_string_to_float(tds_[8].text),

                    }
                    
                    
                    data.append(curr_data)

                conn = sqlite3.connect('stocktrade.db')
                cursor = conn.cursor()

                for row in data:  
                    symbol = row["symbol"]
                    ltp = row["ltp"]
                    change = row["change"]
                    open_price = row["open"]
                    high = row["high"]
                    low = row["low"]
                    volume = row["volume"]
                    close = row["close"]
                    change_percent = row["change_percent"]

                    sql = f"INSERT INTO rawstock (symbol, ltp, change, open, high, low, volume, close, change_percent) VALUES ('{symbol}', {ltp}, {change}, {open_price}, {high},{low}, {volume},{close},{change_percent})"
                    cursor.execute(sql)
                conn.commit()
                conn.close()



                push_to_database(data, last_updated)
                update_last_updated(last_updated)
                driver.close()

    except Exception as e:
        print(e)
        driver.close()




if __name__ == "__main__":
    sync_data()

  