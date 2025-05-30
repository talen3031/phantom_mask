
from flask import Blueprint, jsonify, request
from db import get_db
from flask import Flask, jsonify,request
import sqlite3
import re
import datetime
mask_bp = Blueprint('mask', __name__)

# 查詢所有口罩
@mask_bp.route('/masks', methods=['GET'])
def list_all_masks():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM mask')
    users = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(users)

# 2. 列出指定藥局所販售的所有口罩，並可依照口罩名稱或價格排序。

@mask_bp.route('/pharmacy/<int:pharmacy_id>/masks', methods=['GET'])
def list_masks(pharmacy_id):

    sort = request.args.get('sort', 'name')            #預設名稱
    order = request.args.get('order', 'asc').lower()  # 預設升冪，小寫

    # 檢查參數合法性
    if sort not in ('name', 'price'):
        return jsonify({"error": "sort must be 'name' or 'price'"}), 400

    if order not in ('asc', 'desc'):
        return jsonify({"error": "order must be 'asc' or 'desc'"}), 400
    
    conn = get_db()
    cur = conn.cursor()
    # 確認 pharmacy_id 是否存在    

    cur.execute("SELECT 1 FROM pharmacy WHERE id = ?", (pharmacy_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": f"pharmacy {pharmacy_id} not found"}), 404
    
    #轉成大寫
    order=order.upper()
    
    # 開始查詢
    query = f"""
        SELECT *
        FROM mask
        WHERE pharmacy_id=?
        ORDER BY {sort} {order}
    """    
    
    cur.execute(query, (pharmacy_id,))
    masks = [dict(row) for row in cur.fetchall()]
    
    conn.close()
    
    return jsonify(masks)