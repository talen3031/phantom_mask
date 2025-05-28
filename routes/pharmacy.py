
from flask import Blueprint, jsonify, request
from db import get_db
from flask import Flask, jsonify,request
import sqlite3
import re
import datetime
pharmacy_bp = Blueprint('pharmacy', __name__)
#查詢所有藥局
@pharmacy_bp.route('/pharmacies', methods=['GET'])
def list_pharmacies():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM pharmacy')
    rows = cur.fetchall()
    conn.close()

    # 把每一列 Row 轉成 dict，最後變成 list 傳回前端
    pharmacies = [dict(row) for row in rows]
    return jsonify(pharmacies)

#1.查詢依指定時間與星期幾列出有營業的藥局
@pharmacy_bp.route('/pharmacies/open', methods=['GET'])
def list_open_pharmacies():
    
    day = request.args.get('day')  # 例如 'Mon'
    time = request.args.get('time')  # 例如 '15:30'
    
    valid_days = ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']
    time_pattern = re.compile(r'^\d{2}:\d{2}$')  # 格式必須為兩位數:兩位數

     # 檢查參數是否存在
    if not day or not time:
        return jsonify({"error": "please enter  day, time"}), 400

    # 檢查 day 是否正確
    if day not in valid_days:
        return jsonify({"error": "please enter  day in correct format(ex.Mon)"}), 400

    # 檢查 time 格式
    if not time_pattern.match(time):
        return jsonify({"error": "please enter  time in correct format(00:00~23:59) (ex.14:30)"}), 400

    # 進階：檢查 HH 和 MM 合理範圍
    hour, minute = map(int, time.split(':'))
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return jsonify({"error": "please enter  time in correct format (00:00~23:59) (ex.14:30) "}), 400


    conn = get_db()
    cur = conn.cursor()
    # 開始查詢
    query = """
        SELECT DISTINCT p.*
        FROM pharmacy p
        JOIN opening_hour o ON p.id = o.pharmacy_id
        WHERE o.day_of_week = ?
          AND o.open_time <= ?
          AND o.close_time >= ?
    """
    cur.execute(query, (day, time, time))
    rows = cur.fetchall()
    conn.close()
    pharmacies = [dict(row) for row in rows]
    return jsonify(pharmacies)



#3.找出販售口罩數量（種類）在特定價格範圍內，多於（或少於）X 種的藥局
@pharmacy_bp.route('/pharmacies/mask_count', methods=['GET'])
def pharmacies_by_mask_count():
    # 參數檢查
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    count = request.args.get('count')
    op = request.args.get('op')  # 'gt', 'lt', 'ge', 'le', 'eq'

    # 必填參數檢查
    if not all([min_price, max_price, count, op]):
        return jsonify({"error": "please enter min_price, max_price, count, op"}), 400

    # 驗證數值格式
    try:
        min_price = float(min_price)
        max_price = float(max_price)
        count = int(count)
    except:
        return jsonify({"error": "please enter min_price, max_price, count in correct way"}), 400

    # 支援的 op
    op_map = {
        'gt': '>',
        'lt': '<',
        'ge': '>=',
        'le': '<=',
        'eq': '='
    }
    if op not in op_map:
        return jsonify({"error": "op must be gt, lt, ge, le, eq , one of them."}), 400

    having_sql = f'mask_count {op_map[op]} ?'

    query = f'''
        SELECT
            pharmacy.id,
            pharmacy.name,
            pharmacy.cash_balance,
            COUNT(mask.id) as mask_count
        FROM
            pharmacy
        JOIN
            mask ON pharmacy.id = mask.pharmacy_id
        WHERE
            mask.price BETWEEN ? AND ?
        GROUP BY
            pharmacy.id
        HAVING
            {having_sql}
    '''
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, (min_price, max_price, count))
    rows = cur.fetchall()
    conn.close()

    result = [dict(row) for row in rows]
    return jsonify(result)

#6.依名稱搜尋藥局或口罩，並依照與搜尋關鍵字的相關性排序結果。

@pharmacy_bp.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword')
    search_type = request.args.get('type')  # 'pharmacy' or 'mask'
    if not keyword or not search_type or search_type not in ('pharmacy', 'mask'):
        return jsonify({"error": "please enter keyword or type (pharmacy or mask)"}), 400

    conn = get_db()
    cur = conn.cursor()

    if search_type == 'pharmacy':
        # 關聯性分數規則：開頭=100分，中間有=10分，僅like=5分
        sql = '''
            SELECT *,
                CASE
                    WHEN name = ? THEN 100
                    WHEN name LIKE ? THEN 10
                    WHEN name LIKE ? THEN 5
                    ELSE 0
                END as relevance
            FROM pharmacy
            WHERE name LIKE ?
            ORDER BY relevance DESC, name ASC
        '''
        params = (
            keyword,
            f'{keyword}%',   # 開頭
            f'%{keyword}%',  # 中間
            f'%{keyword}%'   # 樣本
        )
        cur.execute(sql, params)
        result = [dict(row) for row in cur.fetchall()]

    elif search_type == 'mask':
        sql = '''
            SELECT *,
                CASE
                    WHEN name = ? THEN 100
                    WHEN name LIKE ? THEN 10
                    WHEN name LIKE ? THEN 5
                    ELSE 0
                END as relevance
            FROM mask
            WHERE name LIKE ?
            ORDER BY relevance DESC, name ASC
        '''
        params = (
            keyword,
            f'{keyword}%',
            f'%{keyword}%',
            f'%{keyword}%'
        )
        cur.execute(sql, params)
        result = [dict(row) for row in cur.fetchall()]

    conn.close()
    return jsonify(result)

