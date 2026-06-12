import urllib.request
import csv
import json

url = 'https://archives.nseindia.com/content/indices/ind_nifty500list.csv'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8').splitlines()
    
    symbols = []
    reader = csv.reader(content)
    next(reader) # skip header
    for row in reader:
        # row[2] is Symbol, row[0] is Company Name
        symbols.append(f"{row[2]} - {row[0]}")
        
    with open('utils/nifty_symbols.py', 'w') as f:
        f.write('NIFTY_500_SYMBOLS = \\\n')
        f.write(json.dumps(symbols, indent=4))
        f.write('\n')
    print('Saved nifty_symbols.py')
except Exception as e:
    print('Failed:', e)
