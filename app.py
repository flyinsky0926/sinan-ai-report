from flask import Flask
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

BROKER_ID = os.getenv("BROKER_ID")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")


@app.route("/")
def home():
    return "AI 戰報系統正常"


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

            # 開登入頁
            page.goto("https://broker.s338.com.tw/")

            page.wait_for_timeout(10000)

            # 直接輸入帳密
            page.keyboard.press("Tab")
            page.keyboard.type(BROKER_ID)

            page.keyboard.press("Tab")
            page.keyboard.type(BROKER_PASSWORD)

            page.keyboard.press("Enter")

            page.wait_for_timeout(10000)

            # 前往業績頁
            page.goto(
                "https://broker.s338.com.tw/Achievement/AchievementListDetail?SType=1"
            )

            page.wait_for_timeout(10000)

            # 抓所有列
            rows = page.locator("table tbody tr")

            count = rows.count()

            html = """
            <html>
            <head>
            <meta charset="UTF-8">
            <style>

            body{
                background:#18256b;
                color:white;
                font-family:Arial;
                padding:40px;
            }

            h1{
                color:#f4d35e;
                text-align:center;
                font-size:72px;
            }

            .card{
                background:#f4d35e;
                color:black;
                border-radius:30px;
                padding:50px;
                margin-top:50px;
            }

            table{
                width:100%;
                border-collapse:collapse;
                margin-top:30px;
                background:white;
                color:black;
            }

            th{
                background:#111;
                color:#f4d35e;
                padding:20px;
                font-size:28px;
            }

            td{
                padding:18px;
                font-size:26px;
                border-bottom:1px solid #ccc;
            }

            </style>
            </head>
            <body>

            <h1>每日單位戰報</h1>

            <div class="card">

            <h2>TOP10 單位績效</h2>

            <table>

            <tr>
            <th>業務員</th>
            <th>件數</th>
            <th>保費</th>
            <th>代理費</th>
            </tr>
            """

            total_case = 0
            total_premium = 0
            total_fee = 0

            for i in range(count):

                try:

                    tds = rows.nth(i).locator("td")

                    if tds.count() < 12:
                        continue

                    name = tds.nth(0).inner_text().strip()
                    status = tds.nth(2).inner_text().strip()

                    if status != "受理":
                        continue

                    case_count = tds.nth(9).inner_text().strip()
                    premium = tds.nth(10).inner_text().strip()
                    fee = tds.nth(11).inner_text().strip()

                    total_case += float(case_count.replace(",", ""))
                    total_premium += float(premium.replace(",", ""))
                    total_fee += float(fee.replace(",", ""))

                    html += f"""
                    <tr>
                    <td>{name}</td>
                    <td>{case_count}</td>
                    <td>{premium}</td>
                    <td>{fee}</td>
                    </tr>
                    """

                except:
                    pass

            html += f"""
            </table>

            <h2 style="margin-top:40px;">
            全單位合計
            </h2>

            <h3>
            件數：{int(total_case)}
            </h3>

            <h3>
            保費：{int(total_premium):,}
            </h3>

            <h3>
            代理費：{int(total_fee):,}
            </h3>

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
