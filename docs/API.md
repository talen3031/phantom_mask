
# Phantom Mask API 

- 所有 API 回傳皆為 JSON 格式。  
- API 伺服器預設位址：`http://127.0.0.1:5000/`

---

## 1.依據星期幾與時間，列出當時有開門的所有藥局
## GET /pharmacies/open 

- **說明**：依據星期幾與時間，列出當時有開門的所有藥局
- **參數**：
    - `day`: (必填) 星期幾縮寫 (Mon, Tue, Wed, Thur, Fri, Sat, Sun)
    - `time`: (必填) 時間 (例如 15:30)
- **回傳**：
    - 藥局陣列（JSON）
- **範例**：
    ```
    GET /pharmacies/open?day=Tue&time=14:30
    ```
- **回傳範例**：
    ```json
    [
      {
        "id": 1,
        "name": "DFW Wellness",
        "cash_balance": 328.41
      }
    ]
    ```

---
## 2.查詢指定藥局的所有口罩，可依名稱或價格排序，並可指定升/降冪
## GET /pharmacy/<pharmacy_id>/masks 

- 說明：查詢指定藥局的所有口罩，可依名稱或價格排序，並可指定升/降冪
- 參數：
    - pharmacy_id: (必填)
    - sort: (選填) 排序依據 name 或 price，預設 name
    - order: (選填) asc 或 desc，預設 asc
- 回傳：
    - 口罩陣列（JSON）
- 範例：
    GET /pharmacy/1/masks?sort=price&order=desc
- 回傳範例：
    ```json
    [
      {
        "id": 3,
        "pharmacy_id": 1,
        "name": "Second Smile (black) (10 per pack)",
        "price": 31.98
      }
    ]
    ```
---

## 3.列出在特定價格範圍內，販售的口罩數量多於或少於 X 種的藥局
## GET /pharmacies/mask_count 

- 說明：列出在特定價格範圍內，販售的口罩數量多於或少於 X 種的藥局
- 參數：
    - min_price: (必填) 最小價格
    - max_price: (必填) 最大價格
    - count: (必填) 比較的口罩種類數 X
    - op: (必填) 運算子，'gt' , 'lt', 'ge', 'le', 'eq'
    - op_map = {
        'gt': '>',
        'lt': '<',
        'ge': '>=',
        'le': '<=',
        'eq': '='
      }
- 回傳：
    - 藥局陣列（JSON），包含 mask_count 欄位
- 範例：
    GET /pharmacies/mask_count?min_price=10&max_price=50&count=2&op=gt
- 回傳範例：
    ```json
    [
      {
        "id": 1,
        "name": "DFW Wellness",
        "cash_balance": 328.41,
        "mask_count": 3
      }
    ]
    ```

---
##　4.查詢特定日期範圍內，總口罩交易金額最高的前 x 位用戶
## GET /users/top_transactions 

- 說明：查詢特定日期範圍內，總口罩交易金額最高的前 x 位用戶
- 參數：
    - start_date: (必填) 起始日期，格式 YYYY-MM-DD
    - end_date: (必填) 結束日期，格式 YYYY-MM-DD
    - top: (必填) 前幾名
- 回傳：
    - 用戶陣列（JSON），含 total_transaction 欄位
- 範例：
    GET /users/top_transactions?start_date=2021-01-01&end_date=2021-01-31&top=3
- 回傳範例：
    ```json
    [
      {
        "id": 1,
        "name": "Yvonne Guerrero",
        "cash_balance": 191.83,
        "total_transaction": 72.5
      }
    ]
    ```


---
## 5.計算在特定日期範圍內，總共販售的口罩數量與交易金額總額
## GET /transactions/summary 

- 說明：計算在特定日期範圍內，總共販售的口罩數量與交易金額總額
- 參數：
    - start_date: (必填) 起始日期，格式 YYYY-MM-DD
    - end_date: (必填) 結束日期，格式 YYYY-MM-DD
- 回傳：
    - JSON 物件，包含 total_quantity（總數量）、total_transaction（總金額）
- 範例：
    GET /purchase/summary?start_date=2021-01-01&end_date=2021-01-31
- 回傳範例：
    ```json
    {
      "total_quantity": 123,
      "total_transaction": 1983.5
    }
    ```
---
## 6.依名稱搜尋藥局或口罩，並依與關鍵字相關性排序結果
## GET /search 

- 說明：依名稱搜尋藥局或口罩，並依與關鍵字相關性排序結果
- 參數：
    - keyword: (必填) 搜尋關鍵字
    - type: (必填) 搜尋對象 'pharmacy' 或 'mask'
- 回傳：
    - 搜尋結果陣列（JSON），含 relevance 欄位
- 範例：
    GET /search?keyword=Smile&type=mask
- 回傳範例：
    ```json
    [
      {
        "id": 4,
        "pharmacy_id": 1,
        "name": "Second Smile (black) (3 per pack)",
        "price": 5.84,
        "relevance": 10
      }
    ]
    ```
---

## 7.處理用戶購買口罩的過程
## POST /purchase

- 說明：處理用戶購買口罩的過程，可同時從多個藥局購買
- 輸入：
    - user_id: 用戶ID
    - items: 陣列，每個元素 { pharmacy_id, mask_id, quantity }
- 回傳：
    - success: 是否成功
    - total_cost: 本次交易總金額
    - purchases: 每一項商品購買明細
- 範例輸入：
    ```json
    {
      "user_id": 1,
      "items": [
        { "pharmacy_id": 1, "mask_id": 2, "quantity": 3 }
      ]
    }
    ```

- 或是在cmd輸入下列字元:
    - curl -X POST http://127.0.0.1:5000/purchase -H "Content-Type: application/json" -d "{\"user_id\": 1, \"items\":[{\"pharmacy_id\": 1, \"mask_id\": 2, \"quantity\": 3}]}"


- 回傳範例：
    ```json
    {
      "success": true,
      "total_cost": 180.2,
      "purchases": [
        {
          "pharmacy_id": 1,
          "mask_id": 2,
          "mask_name": "Second Smile (black) (10 per pack)",
          "price": 41.86,
          "quantity": 3,
          "total_price": 125.58
        },
        {
          "pharmacy_id": 2,
          "mask_id": 8,
          "mask_name": "Masquerade (green) (3 per pack)",
          "price": 9.4,
          "quantity": 2,
          "total_price": 18.8
        }
      ]
    }
    ```
- 若失敗：
    ```json
    { "error": "用戶餘額不足" }
    ```
---

