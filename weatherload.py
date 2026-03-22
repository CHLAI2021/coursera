# import modules
import sqlite3
import json
import time
import requests 

# set api and service url
api_key = "9b030faa18a0fbd2687072e48cbd7a09"
service_url = "https://api.openweathermap.org/data/2.5/weather"

# connect sql file and create read & write cursor
conn = sqlite3.connect('opengeo1.sqlite')
read_cur = conn.cursor()
write_cur = conn.cursor()

# create table include addess temp 
read_cur.execute('''CREATE TABLE IF NOT EXISTS Weather(
                 address TEXT UNIQUE,
                 temp REAL,
                 description TEXT,
                 updated_at TEXT 
                 )''')
# selct address,geodata and set count
read_cur.execute('SELECT address,geodata FROM Locations')
count = 0

# read each row 
for row in read_cur:
    if count > 50: 
        print('pausing a bit')
        break
    address = row[0] # extract address
    if isinstance(address,bytes): # keep data type the same
        address = address.decode('utf8')
    geodata_str = row[1] # extract geodata
    try:
        js = json.loads(geodata_str) # json parse geodata
        if not js or 'features' not in js or len(js['features']) == 0: # ensure features in js
            continue
        # extract lat & lon
        lat = js['features'][0]['geometry']['coordinates'][1]
        lon = js['features'][0]['geometry']['coordinates'][0]

    except Exception as e:
        print(f"json parse fail")
        continue

    print(f"{count+1}: {address} {lat} {lon}",end =" ")  

    # set params 
    my_params = {
        "lat" : lat,
        "lon" : lon,
        "appid" : api_key,
        "units" : "metric",
        "lang" : "zh-TW"
    }
    # send request to service 
    try:
        response = requests.get(service_url , params = my_params , timeout = 5)
        print(f"\n {response.url}")
        print(f"-"*30)
        if response.status_code == 200:
            data = response.json()
            try:
                count = count + 1  # sucess count plus 1
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                # update address,temp,description data & use sql saving  time_at
                sql = '''INSERT OR REPLACE INTO Weather(address,temp,description,updated_at) VALUES(?,?,?,datetime('now','localtime'))'''
                write_cur.execute(sql,(address,temp,desc))
                conn.commit()
            except (KeyError,IndexError) as e:
                print(f"not found keys")
                continue
            print(f"溫度{temp},{desc}")
            if count % 10 == 0:
                print(f"pausing a bit")
                time.sleep(5)
        else:
            print(f"fail to get data : {response.status_code},{response.text}")
            break

    except Exception as e:
        print(f"reject the request : {e}")
        continue

print(f"can go to next step geodump")

# close cur and sql
read_cur.close()
write_cur.close()
conn.close()