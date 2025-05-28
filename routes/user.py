
from flask import Blueprint, jsonify, request
from db import get_db
from flask import Flask, jsonify,request
import sqlite3
import re
import datetime
user_bp = Blueprint('user', __name__)


# 查詢所有使用者
@user_bp.route('/users', methods=['GET'])
def list_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM user')
    users = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(users)

# 查詢某使用者所有購買紀錄
@user_bp.route('/user/<int:user_id>/purchases', methods=['GET'])
def user_purchases(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM purchase WHERE user_id=?', (user_id,))
    purchases = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(purchases)

#4.查詢特定日期範圍內，總口罩交易金額最高的前 x 位用戶。
@user_bp.route('/users/top_transactions', methods=['GET'])
def top_users_by_transaction():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    top = request.args.get('top', 5)  # 可選預設5名

    # 檢查參數
    if not start_date or not end_date or not top:
        return jsonify({"error": "please enter start_date, end_date, top "}), 400
    
    
    # 嚴格檢查日期格式
    try:
        start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "start_date, end_date must be in YYYY-MM-DD format"}), 400

    # 開始日不得晚於結束日
    if start_dt > end_dt:
        return jsonify({"error": "start_date cannot be after end_date"}), 400

    #檢查x須為整數
    try:
        top = int(top)
    except:
        return jsonify({"error": "top must be integer"}), 400


    sql = '''
        SELECT
            user.id,
            user.name,
            user.cash_balance,
            SUM(purchase.total_price) AS total_transaction
        FROM
            user
        JOIN
            purchase ON user.id = purchase.user_id
        WHERE
            purchase.transaction_date BETWEEN ? AND ?
        GROUP BY
            user.id
        ORDER BY
            total_transaction DESC
        LIMIT ?
    '''
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, (start_date, end_date, top))
    rows = cur.fetchall()
    conn.close()

    result = [dict(row) for row in rows]
    return jsonify(result)