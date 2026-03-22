# import modules
import urllib.request,urllib.parse,urllib.error
import sqlite3
import ssl,json,time

#https://py4e-data.dr-chuck.net/opengeo?q=Ann+Arbor%2C+MI
serviceurl = 'https://py4e-data.dr-chuck.net/opengeo?'

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# create and handle sql file
conn = sqlite3.connect('opengeo1.sqlite')
cur = conn.cursor()

# check talbe and create
cur.execute(''' CREATE TABLE IF NOT EXISTS Locations(address TEXT,geodata TEXT)''')

# save where data
fh = open('where.data')

# intial variables
count = 0
notfound = 0

# read fh
for line in fh:
    if count > 100 :  # limit : 100 data to break
        print('Retrieved 100 locations ,restart to retrieve more')
        break

    address = line.strip() # remove blank
    if len(address) < 1 : continue
    print('')
    cur.execute('SELECT geodata FROM Locations WHERE address = ? ',(memoryview(address.encode()),))

    try:
        geodata = cur.fetchone()[0]
        print('Found in database',address)
        continue  # next data
    except:
        pass # next step ask for data from server
    
    # create parms dict for query
    parms = dict()
    parms['q'] = address
    url = serviceurl + urllib.parse.urlencode(parms)
    uh = urllib.request.urlopen(url,context=ctx) # ask request to server
    try:
        data = uh.read().decode()
        print(f"Retrieving {len(data)},characters {data[:20].replace('\n',' ')}")
        count = count + 1  # count num ask for server 
    except Exception as e:
        print(f'Url decode error: {e} ,{url}')
        continue
    try:
        js =json.loads(data)
    except:
        print(f'Json parse fail, {data}')
        continue

    if not js or 'features' not in js:
        print(f'== Download error == , {data}')
        break # not right format  need break to check
     
    if len(js['features']) == 0:
        print(f'== Object not found  == , {data}')
        notfound = notfound + 1
        
    cur.execute(''' INSERT INTO Locations(address,geodata)VALUES(?,?)''',
                (memoryview(address.encode()),memoryview(data.encode())))
    conn.commit()

    if count % 10 == 0:
        print('Pausing for a bit...')
        time.sleep(5)

if notfound > 0:
    print(f'Number of features for which the location could not be found: {notfound}')

print('can go to the next step to get weather data.')




