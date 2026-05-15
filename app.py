from flask import Flask
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

BROKER_ID = os.getenv("BROKER_ID")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")

@app.route("/")
def home():
    return "AI 戰報系統正常運行"

@app.route("/run")
def run():

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox"]
            )

            page = browser.new_page(
                viewport={"width": 1400, "height": 1000}
            )

            # 進登入頁
            page.goto("https://broker.s338.com.tw/")

            page.wait_for_timeout(8000)

            # 點帳號框
            page.mouse.click(720, 470)

            page.keyboard.type(BROKER_ID)

            page.wait_for_timeout(1000)

            # 點密碼框
            page.mouse.click(720, 540)

            page.keyboard.type(BROKER_PASSWORD)

            page.wait_for_timeout(1000)

            # 點登入
            page.mouse.click(720, 650)

            page.wait_for_timeout(10000)

            # 進業績頁
            page.goto(
                "https://broker.s338.com.tw/Achievement/AchievementListDetail?SType=1"
            )

            page.wait_for_timeout(10000)

            rows = page.locator("table tbody tr")

            count = rows.count()

            cards = ""

            total_case = 0
            total_premium = 0
            total_fee = 0

            rank = 1

            for i in range(count):

                try:

                    cols = rows.nth(i).locator("td")

                    name = cols.nth(0).inner_text().strip()
                    status = cols.nth(2).inner_text().strip()

                    if status != "受理":
                        continue

                    case_count = cols.nth(9).inner_text().strip()
                    premium = cols.nth(10).inner_text().strip()
                    fee = cols.nth(11).inner_text().strip()

                    total_case += float(case_count.replace(",", ""))
                    total_premium += float(premium.replace(",", ""))
                    total_fee += float(fee.replace(",", ""))

                    cards += f"""
                    <div class="card">
                        <div class="rank">#{rank}</div>
                        <div class="name">{name}</div>
                        <div class="info">件數：{case_count}</div>
                        <div class="info">保費：{premium}</div>
                        <div class="info">代理費：{fee}</div>
                    </div>
                    """

                    rank += 1

                except:
                    pass

            html = f"""
            <html>
            <head>
            <meta charset="UTF-8">

            <style>

            body {{
                margin:0;
                padding:40px;
                font-family:Microsoft JhengHei;
                background:linear-gradient(180deg,#08133d,#1d2f7a);
                color:white;
            }}

            .title {{
                text-align:center;
                font-size:72px;
                color:#ffd95a;
                font-weight:bold;
            }}

            .sub {{
                text-align:center;
                font-size:28px;
                margin-bottom:40px;
            }}

            .grid {{
                display:grid;
                grid-template-columns:repeat(2,1fr);
                gap:20px;
            }}

            .card {{
                background:rgba(255,255,255,0.08);
                border:2px solid #ffd95a;
                border-radius:20px;
                padding:25px;
            }}

            .rank {{
                color:#ffd95a;
                font-size:34px;
                font-weight:bold;
            }}

            .name {{
                font-size:42px;
                font-weight:bold;
                margin:15px 0;
            }}

            .info {{
                font-size:28px;
                line-height:1.8;
            }}

            .total {{
                margin-top:40px;
                background:#ffd95a;
                color:#111;
                border-radius:20px;
                padding:30px;
                text-align:center;
                font-size:32px;
                font-weight:bold;
            }}

            </style>
            </head>

            <body>

            <div class="title">
            每日單位戰報
            </div>

            <div class="sub">
            信安雲林 AI 自動戰報
            </div>

            <div class="grid">
            {cards}
            </div>

            <div class="total">
            全單位合計<br><br>

            件數：{int(total_case)}<br>
            保費：{int(total_premium):,}<br>
            代理費：{int(total_fee):,}
            </div>

            </body>
            </html>
            """

            browser.close()

            return html

    except Exception as e:

        return f"錯誤：{str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
    
