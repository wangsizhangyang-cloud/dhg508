import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
c = sqlite3.connect(r'E:\508\dhg508-workspace\projects\forbidden_city\forbidden_city.db')
c.row_factory = sqlite3.Row
cur = c.cursor()
cur.execute("SELECT * FROM facts_view WHERE building_eng='Meridian Gate' ORDER BY year")
for r in cur.fetchall():
    print('---- id', r['id'], '| year', r['year'], '| date', r['date'])
    print('fact:', r['fact'])
    print('people:', r['people'], '| place:', r['place'])
    print('source:', r['source'], '| locator:', r['source_locator'])
    print('url:', r['source_url'])
    print('note:', r['note'])
