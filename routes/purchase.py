
from flask import Blueprint, jsonify, request
from db import get_db
from flask import Flask, jsonify,request
import sqlite3
import re
import datetime
purchase_bp = Blueprint('purchase', __name__)
# 查詢所有購買紀錄
@purchase_bp.route('/purchases', methods=['GET'])
def list_purchases():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM purchase')
    users = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(users)

#5.計算在特定日期範圍內，總共販售的口罩數量與交易金額總額。

@purchase_bp.route('/purchase/summary', methods=['GET'])
def transaction_summary():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if not start_date or not end_date:
        return jsonify({"error": "please enter start_date, end_date"}), 400
 
    # 嚴格檢查日期格式
    try:
        start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "start_date, end_date must be in YYYY-MM-DD format"}), 400

    # 開始日不得晚於結束日
    if start_dt > end_dt:
        return jsonify({"error": "start_date cannot be after end_date"}), 400

    sql = '''
        SELECT
            SUM(purchase.quantity) as total_quantity,
            SUM(purchase.total_price) as total_transaction
        FROM
            purchase
        WHERE
            purchase.transaction_date BETWEEN ? AND ?
    '''
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, (start_date, end_date))
    row = cur.fetchone()
    conn.close()

    # 預防沒有資料時 row 為 None
    total_quantity = row['total_quantity'] if row['total_quantity'] is not None else 0
    total_transaction = row['total_transaction'] if row['total_transaction'] is not None else 0

    return jsonify([{
        "total_quantity": total_quantity,
        "total_transaction": total_transaction
    }])


#7.處理用戶購買口罩的過程

@purchase_bp.route('/purchase', methods=['POST'])
def purchase():
    data = request.get_json()
    user_id = data.get('user_id')
    items = data.get('items')

    if not user_id or not items or not isinstance(items, list):
        return jsonify({"error": "please enter user_id and items"}), 400

    conn = get_db()
    cur = conn.cursor()

    try:
        # 取得用戶現有餘額
        cur.execute("SELECT cash_balance FROM user WHERE id=?", (user_id,))
        user_row = cur.fetchone()
        if not user_row:
            conn.close()
            #找不到用戶
            return jsonify({"error": f"can't found the user{user_id}"}), 404

        user_balance = user_row['cash_balance']
        total_cost = 0
        purchase_detail = []

        # 計算所有商品總金額
        for item in items:
            mask_id = item.get('mask_id')
            pharmacy_id = item.get('pharmacy_id')
            quantity = item.get('quantity')

            # 查口罩價格
            cur.execute("SELECT name, price FROM mask WHERE id=? AND pharmacy_id=?", (mask_id, pharmacy_id))
            mask = cur.fetchone()
            if not mask:
                conn.close()
                return jsonify({"error": f"pharmacy {pharmacy_id} doesn't have mask{mask_id}"}), 404

            item_cost = mask['price'] * quantity
            total_cost += item_cost
            purchase_detail.append({
                "pharmacy_id": pharmacy_id,
                "mask_id": mask_id,
                "mask_name": mask['name'],
                "price": mask['price'],
                "quantity": quantity,
                "total_price": item_cost
            })

        if user_balance < total_cost:
            conn.close()
            return jsonify({"error": "user balance isn't enough"}), 400

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for detail in purchase_detail:
            # 藥局加錢
            cur.execute("UPDATE pharmacy SET cash_balance = cash_balance + ? WHERE id=?",
                        (detail['total_price'], detail['pharmacy_id']))
            # 寫入 purchase 紀錄
            cur.execute(
                "INSERT INTO purchase (user_id, pharmacy_id, mask_name, quantity, total_price, transaction_date) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, detail['pharmacy_id'], detail['mask_name'], detail['quantity'], detail['total_price'], now_str)
            )

        # 扣用戶餘額
        cur.execute("UPDATE user SET cash_balance = cash_balance - ? WHERE id=?", (total_cost, user_id))

        conn.commit()
        conn.close()
        return jsonify({"success": True, "total_cost": total_cost, "purchases": purchase_detail}), 200

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": f"transanction failed: {str(e)}"}), 500
