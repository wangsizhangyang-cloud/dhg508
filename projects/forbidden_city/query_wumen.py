import sqlite3
conn = sqlite3.connect('forbidden_city.db')
cur = conn.cursor()
cur.execute("SELECT id, building, year, date, fact, people, place, source, source_locator, note FROM facts_view WHERE building LIKE '%午%'")
for r in cur.fetchall():
    print(r)
