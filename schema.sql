CREATE TABLE IF NOT EXISTS pharmacy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    cash_balance REAL
);

CREATE TABLE IF NOT EXISTS opening_hour (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pharmacy_id INTEGER,
    day_of_week TEXT,
    open_time TEXT,
    close_time TEXT,
    FOREIGN KEY(pharmacy_id) REFERENCES pharmacy(id)
);

CREATE TABLE IF NOT EXISTS mask (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pharmacy_id INTEGER,
    name TEXT ,
    price REAL,
    FOREIGN KEY(pharmacy_id) REFERENCES pharmacy(id)
    UNIQUE (pharmacy_id, name)
);


CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    cash_balance REAL
);

CREATE TABLE IF NOT EXISTS purchase (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    pharmacy_id INTEGER,
    mask_name TEXT,
    quantity INTEGER,
    total_price REAL,
    transaction_date TEXT,
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(pharmacy_id) REFERENCES pharmacy(id)
);
