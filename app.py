import sqlite3
import requests
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Данные твоего бота
TELEGRAM_TOKEN = "8747524473:AAG20LH6Pdkw0DwOg0OHj0tNhqQO4fEpy7Q"
CHAT_ID = "6915077397"

def init_db():
    conn = sqlite3.connect('defense.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact TEXT, plan TEXT, txid TEXT
        )
    ''')
    conn.commit()
    conn.close()

def send_telegram_msg(contact, plan, txid):
    text = (f"🛡️ **PSIXOGEN: NEW ORDER**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📱 **TG:** {contact}\n"
            f"💎 **PLAN:** {plan}\n"
            f"🔗 **DATA/TXID:** {txid}\n"
            f"━━━━━━━━━━━━━━━")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except:
        pass

@app.route('/')
def index():
    # Инициализируем базу при первом заходе, если её нет
    init_db()
    return render_template('index.html')

@app.route('/order', methods=['POST'])
def create_order():
    contact = request.form.get('contact')
    plan = request.form.get('plan')
    txid = request.form.get('txid')

    send_telegram_msg(contact, plan, txid)

    conn = sqlite3.connect('defense.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (contact, plan, txid) VALUES (?, ?, ?)",
                   (contact, plan, txid))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

# В самом низу app.py оставь только это:
if __name__ == "__main__":
    app.run()