from flask import Flask, send_file
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

    report_html = ""

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox"]
            )

            page = browser.new_page()

            # 登入
            page.goto("https://broker.s338.com.tw/")

            page.wait_for_timeout(3000)

            page.locator('input[type="text"]').nth(1).fill(BROKER_ID)

            page.locator('input[type="password"]').fill(BROKER_PASSWORD)

            page.keyboard.press("Enter")

            page.wait_for_timeout(5000)

            # 業績頁
            page.goto(
                "https://broker.s338.com.tw/Achievement/AchievementListDetail?SType=1"
            )

            page.wait_for_timeout(5000)

            rows = page.locator("table tbody tr")

            count = rows.count()

            total_case = 0
            total_premium = 0
            total_fee = 0

            for i in range(count):

                try:

                    name = rows.nth(i).locator("td").nth(0).inner_text().strip()

                    status = rows.nth(i).locator("td").nth(2).inner_text().strip()

                    if status != "受理":
                        continue

                    case_count = rows.nth(i).locator("td").nth(9).inner_text().strip()

                    premium = rows.nth(i).locator("td").nth(10).inner_text().strip()

                    fee = rows.nth(i).locator("td").nth(11).inner_text().strip()

                    total_case += float(case_count.replace(",", ""))

                    total_premium += float(premium.replace(",", ""))

                    total_fee += float(fee.replace(",", ""))

                    report_html += f"""
                    <div class="row">
                        <div>{name}</div>
                        <div>{case_count}件</div>
                        <div>{premium}</div>
                        <div>{fee}</div>
                    </div>
                    """

                except:
                    pass

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">

            <style>

            body {{
                width: 1080px;
                height: 1920px;
                margin: 0;
                padding: 60px;
                box-sizing: border-box;
                background: linear-gradient(#091540,#1b3c88);
                color: white;
                font-family: sans-serif;
            }}

            .title {{
                font-size: 70px;
                font-weight: bold;
                margin-bottom: 40px;
            }}

            .table {{
                background: rgba(255,255,255,0.1);
                border-radius: 30px;
                padding: 30px;
            }}

            .row {{
                display:flex;
                justify-content:space-between;
                padding:20px 0;
                border-bottom:1px solid rgba(255,255,255,0.2);
                font-size:32px;
            }}

            .total {{
                margin-top:40px;
                font-size:42px;
                color:yellow;
                line-height:1.8;
            }}

            </style>
            </head>

            <body>

            <div class="title">
            信安雲林 每日單位戰報
            </div>

            <div class="table">

            {report_html}

            <div class="total">
            全單位合計<br>
            件數：{int(total_case)}<br>
            保費：{int(total_premium):,}<br>
            代理費：{int(total_fee):,}
            </div>

            </div>

            </body>
            </html>
            """

            with open("report.html", "w", encoding="utf-8") as f:
                f.write(html)

            page2 = browser.new_page(
                viewport={"width":1080,"height":1920}
            )

            page2.goto("file:///app/report.html")

            page2.screenshot(
                path="battle_report.png",
                full_page=True
            )

            browser.close()

        return "AI 戰報生成成功"

    except Exception as e:

        return f"錯誤：{str(e)}"


@app.route("/report")
def report():

    return send_file(
        "battle_report.png",
        mimetype="image/png"
    )


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(host="0.0.0.0", port=port)
