# import modules 
import sqlite3
import json
import codecs

# 建立opengeo1 資料連結及天氣與地點雙游標
conn = sqlite3.connect('opengeo1.sqlite')
weather_cur = conn.cursor()
location_cur = conn.cursor()

# 使用天氣游標選取天氣表格資料
weather_cur.execute('SELECT address,temp,description,updated_at FROM Weather')

# 利用codecs建立fhand 文件載入文件 執行模式 與資料型態
fhand = codecs.open('where.js','w','utf-8')

# 開頭 myData 換行寫入fhand
fhand.write('myData = [\n')

# 設置行數計數器 & 設置無法建置座標天氣計數器
line_count = 0
not_found = 0

# 開始跑天氣表格每一行資料
for row in weather_cur:
    # 獲取address,temp,desc,updated_at 資料
    address = row[0]
    temp = row[1]
    desc = row[2]
    updated_at =row[3]

    # 使用地點cur 執行address 到地點table 查找geodata(注意需切換為bytes)
    location_cur.execute('SELECT geodata FROM Locations WHERE address=?',(memoryview(address.encode()),))

    # 存取geodata_row =>if  fail : notfound +1 & next
    try:
        geodata_row = location_cur.fetchone()[0]

    except Exception as e:
        print(f"not found geodata:{e}")
        not_found = not_found + 1
        continue

    # geodata_row 重新decode 存入 data 並將data 使用json 解析 => fail: notfound +1 & next
    data = geodata_row.decode()
    try:
        js = json.loads(data)

    except Exception as e:
        print(f"json parse fail")
        not_found = not_found + 1
        continue

    # if 'features' 沒資料 =>notfound +1 & next
    if len(js['features']) == 0:
        print(f"object not found")
        not_found = not_found + 1
        continue

    # 獲取lat lon  => fail  : notfound +1 & next  
    try:
        lat = js['features'][0]['geometry']['coordinates'][1]
        lon = js['features'][0]['geometry']['coordinates'][0]   
        # 獲取 where 這裡可以加圖 用br 做間隔 & 處理xxx’s 的地點會遇到blow up
        where = f" 📌 {address} <br> 🌡️  {temp} °C ,{desc} <br> 🕰️  {updated_at} " 
        where = where.replace("'","") 

    except (KeyError,IndexError) as e:
        print(f"not foune the key")
        not_found = not_found + 1
        continue
    
    # 打印結果(lat lon where) =>  fail  : notfound +1 & next
    # 針對文件當>0 時須先加上逗號再換行做處理
    try:
        print(lat , lon, where)
        if line_count > 0 :
            fhand.write(',\n')
        output = f"[{lat},{lon},'{where}']" # 將lat lon where 存入 output
        fhand.write(output)
        line_count = line_count + 1   # 執行寫入成功，行數計數器+1 

    except Exception as e:
        print(f"not get location")
        not_found = not_found + 1
        continue
# 文件作結束
fhand.write('\n];\n')
# 雙游標關閉
weather_cur.close()
location_cur.close()
#文件關閉
conn.close()

print(f"-"*30)
print(f"{line_count} ,records written to where.js")
print(f"the location could not be found: {not_found}")
print(f"Open where.html to view the data in a browser")







