import sqlite3
import requests
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# 1. База данных
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# 2. Конфиг ТГ
TELEGRAM_TOKEN = "8747524473:AAG20LH6Pdkw0DwOg0OHj0tNhqQO4fEpy7Q"
CHAT_ID = "6915077397"
templates = Jinja2Templates(directory="templates")

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

# 3. Роуты
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/order")
async def create_order(contact: str = Form(...), plan: str = Form(...), txid: str = Form(...)):
    send_telegram_msg(contact, plan, txid)
    conn = sqlite3.connect('defense.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (contact, plan, txid) VALUES (?, ?, ?)", (contact, plan, txid))
    conn.commit()
    conn.close()
    return JSONResponse(content={"status": "success"})

# 4. АВТО-ЗАПУСК (Сам подхватит порт Railway)
if __name__ == "__main__":
    import uvicorn
    # Railway всегда передает порт в переменную окружения PORT
    # Если её нет (локально), включится 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)