from flask import Flask, jsonify,request
import sqlite3
import re
import datetime

from routes.pharmacy import pharmacy_bp
from routes.user import user_bp
from routes.purchase import purchase_bp
from routes.mask import mask_bp

app = Flask(__name__)

# 註冊 blueprint
app.register_blueprint(pharmacy_bp)
app.register_blueprint(user_bp)
app.register_blueprint(mask_bp)
app.register_blueprint(purchase_bp)

if __name__ == '__main__':
    app.run(debug=True)






