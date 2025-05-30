import pytest
import sys
import os
#最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

#1.依據星期幾與時間，列出當時有開門的所有藥局
def test_open_pharmacies_missing_params(client):
    response = client.get('/pharmacies/open')
    assert response.status_code == 400

def test_open_pharmacies_valid(client):
    response = client.get('/pharmacies/open?day=Mon&time=09:00')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

#2.查詢指定藥局的所有口罩，可依名稱或價格排序，並可指定升/降冪
    #pharmacy id 不存在
def test_pharmacies_mask_wrong_pharmacyid(client):
    response = client.get('/pharmacy/5000/masks?sort=price&order=desc')
    assert response.status_code == 404
    
    #sort須為name or price
def test_pharmacies_mask_wrong_param(client):
    response = client.get('/pharmacy/5000/masks?sort=user')
    assert response.status_code == 400

def test_pharmacies_mask_valid(client):
    response = client.get('/pharmacy/1/masks?sort=price&order=desc')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

#3.列出在特定價格範圍內，販售的口罩數量多於或少於 X 種的藥局
    #ex.missig max_price 
def test_pharmacies_mask_count_missing_params(client):
    response = client.get('/pharmacies/mask_count?min_price=10&count=2&op=gt')
    assert response.status_code == 400

def test_pharmacies_mask_count_valid(client):
    response = client.get('/pharmacies/mask_count?min_price=10&max_price=50&count=2&op=gt')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

#4.查詢特定日期範圍內，總口罩交易金額最高的前 x 位用戶
    #top不為整數 ex.top=3.6
def test_users_top_transactions_wrong_x(client):
    response = client.get('/users/top_transactions?start_date=2021-01-01&end_date=2021-01-31&top=3.6')
    assert response.status_code == 400
    
    #起始日大於結束日 ex.start_date=2025-01-01&end_date=2021-01-31
def test_users_top_transactions_wrong_date(client):
    response = client.get('/users/top_transactions?start_date=2025-01-01&end_date=2021-01-31&top=3')
    assert response.status_code == 400

def test_users_top_transactions_valid(client):
    response = client.get('/users/top_transactions?start_date=2021-01-01&end_date=2021-01-31&top=3')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

#5.計算在特定日期範圍內，總共販售的口罩數量與交易金額總額
    #日期格式不正確 ex.start_date=2021-13-01
def test_purchase_summary_wrong_date(client):
    response = client.get('/purchase/summary?start_date=2021-13-01&end_date=2021-01-31')
    assert response.status_code == 400
def test_purchase_summary_valid(client):
    response = client.get('/purchase/summary?start_date=2021-01-01&end_date=2021-01-31')
    assert response.status_code == 200

#6.依名稱搜尋藥局或口罩，並依與關鍵字相關性排序結果
    # type須為'pharmacy' 或 'mask'
def test_search_missing_params(client):
    response = client.get('/search?keyword=Smile&type=price')
    assert response.status_code == 400

def test_search_valid(client):
    response = client.get('/search?keyword=Smile&type=mask')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

#7.處理用戶購買口罩的過程
def test_purchase_missing_params(client):
    # 缺必要參數，應回 400
    rv = client.post('/purchase', json={})
    assert rv.status_code == 400
    assert 'error' in rv.get_json()

def test_purchase_wrong_user_id(client):
    # user_id 不存在
    rv = client.post('/purchase', json={
        "user_id": 99999,  # 假設這個 user_id 不存在
        "items": [
            {"pharmacy_id": 1, "mask_id": 2, "quantity": 1}
        ]
    })
    assert rv.status_code == 404
    assert 'error' in rv.get_json()

def test_purchase_wrong_mask_id(client):
    rv = client.post('/purchase', json={
        "user_id": 1,  
        "items": [
            {"pharmacy_id": 1, "mask_id": 99999, "quantity": 1}  # mask_id 不存在
        ]
    })
    assert rv.status_code == 404
    assert 'error' in rv.get_json()

def test_purchase_insufficient_balance(client):
    # 餘額不足
    rv = client.post('/purchase', json={
        "user_id": 1,  # 已存在的 user
        "items": [
            {"pharmacy_id": 1, "mask_id": 2, "quantity": 99999999999}  # 故意超大金額
        ]
    })
    assert rv.status_code == 400
    assert 'error' in rv.get_json()

def test_purchase_success(client):
    # 成功下單，應回 200
    # 請確認 DB 裡的 user_id、pharmacy_id、mask_id 都存在且餘額夠
    rv = client.post('/purchase', json={
        "user_id": 2,
        "items": [
            {"pharmacy_id": 1, "mask_id": 2, "quantity": 0}
        ]
    })
    assert rv.status_code == 200
    result = rv.get_json()
    assert result['success'] is True
    assert 'total_cost' in result
    assert isinstance(result['purchases'], list)

