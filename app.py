import http.server
import socketserver
import os
import json
import requests

# Конфиг ТГ
TELEGRAM_TOKEN = "8747524473:AAG20LH6Pdkw0DwOg0OHj0tNhqQO4fEpy7Q"
CHAT_ID = "6915077397"

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/order':
            # Читаем JSON от браузера
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            contact = data.get('contact', 'Не указан')
            plan = data.get('plan', 'Не выбран')
            txid = data.get('txid', 'Нет данных')

            # Формируем текст
            text = (f"🛡️ **PSIXOGEN: NEW ORDER**\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📱 **TG:** {contact}\n"
                    f"💎 **PLAN:** {plan}\n"
                    f"🔗 **DATA/TXID:** {txid}\n"
                    f"━━━━━━━━━━━━━━━")

            # Отправляем в ТГ
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

            # Отвечаем браузеру
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("0.0.0.0", port), MyHandler) as httpd:
        print(f"Сервер пашет на порту {port}")
        httpd.serve_forever()