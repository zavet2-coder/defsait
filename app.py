import http.server
import socketserver
import os
import json
import requests

# config
T_TOKEN = os.environ.get("TELEGRAM_TOKEN")
C_ID = os.environ.get("CHAT_ID")
DB_FILE = "ips.txt"

# загрузка базы при старте
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        f.write("")

def get_banned_ips():
    with open(DB_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def add_to_ban(ip):
    with open(DB_FILE, "a") as f:
        f.write(f"{ip}\n")

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/order':
            # достаем реальный IP
            xff = self.headers.get('x-forwarded-for', '')
            ip = xff.split(',')[0].strip() if xff else self.client_address[0]

            # чекаем бан-лист
            if ip in get_banned_ips():
                self.send_response(429)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "limit"}).encode())
                return

            try:
                l = int(self.headers.get('Content-Length', 0))
                raw = self.rfile.read(l)
                d = json.loads(raw)

                u = d.get('contact', '-')
                p = d.get('plan', '-')
                t = d.get('txid', '-')

                if u == '-' or t == '-':
                    self.send_response(400)
                    self.end_headers()
                    return

                # вносим в файл
                add_to_ban(ip)

                # tg send
                txt = (f"🛡️ **PSIXOGEN: NEW ORDER**\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"📱 **TG:** {u}\n"
                       f"💎 **PLAN:** {p}\n"
                       f"🔗 **DATA/TXID:** {t}\n"
                       f"━━━━━━━━━━━━━━━")

                requests.post(
                    f"https://api.telegram.org/bot{T_TOKEN}/sendMessage",
                    json={"chat_id": C_ID, "text": txt, "parse_mode": "Markdown"},
                    timeout=10
                )

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())

            except:
                self.send_response(500)
                self.end_headers()

if __name__ == "__main__":
    p = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("0.0.0.0", p), Handler) as srv:
        print(f"srv up:{p}")
        srv.serve_forever()