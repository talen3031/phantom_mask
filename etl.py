import json
import sqlite3
import re

def parse_opening_hours(opening_hours_str):
    result = []
    segments = opening_hours_str.split('/')

    for seg in segments:
        seg = seg.strip()
        match = re.match(r"([A-Za-z, ]+)\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})", seg)
        if match:
            days_str, open_time, close_time = match.groups()
            days = [d.strip() for d in days_str.split(',')]
            for day in days:
                result.append({
                    "day_of_week": day,
                    "open_time": open_time,
                    "close_time": close_time
                })
    return result

def load_pharmacies(conn, pharmacies):
    for p in pharmacies:
        sql_pharmacies='INSERT OR IGNORE INTO pharmacy (name, cash_balance) VALUES (?, ?)'
        
        cur = conn.cursor()
        cur.execute(sql_pharmacies, 
                    (p['name'], p['cashBalance']))
        pharmacy_id = cur.lastrowid

        # Opening hours
        hours = parse_opening_hours(p['openingHours'])
        sql_opening_hours='INSERT INTO opening_hour (pharmacy_id, day_of_week, open_time, close_time) VALUES (?, ?, ?, ?)'
        for h in hours:
            cur.execute(sql_opening_hours,
                        (pharmacy_id, h['day_of_week'], h['open_time'], h['close_time']))
        # Masks
        sql_masks='INSERT OR IGNORE INTO mask (pharmacy_id, name, price) VALUES (?, ?, ?)'
        for m in p['masks']:
            cur.execute(sql_masks,
                        (pharmacy_id, m['name'], m['price']))
    conn.commit()
    
def load_users(conn, users):
    for u in users:
        cur = conn.cursor()

        sql_user='INSERT INTO user (name, cash_balance) VALUES (?, ?)'

        cur.execute(sql_user, 
                    (u['name'], u['cashBalance']))
        
        user_id = cur.lastrowid
        
        sql_purchase='''INSERT INTO purchase 
                (user_id, pharmacy_id, mask_name, total_price, transaction_date)
                VALUES (?, ?, ?, ?, ?)'''
        
        for h in u.get('purchaseHistories', []):
            cur.execute(sql_purchase,
                (user_id, h['pharmacyName'], h['maskName'], h['transactionAmount'], h['transactionDate'])
            )
    conn.commit()

def main():
    # 開啟資料庫
    conn = sqlite3.connect('pharmacy.db',timeout=10)
    with open('schema.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    
    json1='pharmacies.json'
    json2='users.json'
    
    # 載入JSON
    with open(f'data/{json1}', 'r', encoding='utf-8') as f:
        pharmacies = json.load(f)
    with open(f'data/{json2}', 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    # 載入資料
    print(f"loading data from {json1}...............")
    load_pharmacies(conn, pharmacies)
    print(f"loading data from {json2}...............")
    load_users(conn, users)

    conn.commit()
    conn.close()
    print("ETL Done!")


if __name__ == '__main__':
    main()