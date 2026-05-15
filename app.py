from flask import Flask, send_file
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

BROKER_ID = os.getenv("BROKER_ID")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")


@app.route("/")
def home():
    return "信安 AI 戰報系統正常運行"


@app.route("/run")
def run():

    members = []

    total_case = 0
    total_premium = 0
    total_fee = 0

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox"]
            )

            page = browser.new_page()

            page.goto("https://broker.s338.com.tw/")

            page.wait_for_timeout(3000)

            page.locator('input[type="text"]').nth(1).fill(BROKER_ID)

            page.locator('input[type="password"]').fill(BROKER_PASSWORD)

            page.keyboard.press("Enter")

            page.wait_for_timeout(5000)

            page.goto(
                "https://broker.s338.com.tw/Achievement/AchievementListDetail?SType=1"
            )

            page.wait_for_timeout(5000)

            rows = page.locator("table tbody tr")

            count = rows.count()

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

                    members.append({
                        "name": name,
                        "case": case_count,
                        "premium": premium,
                        "fee": fee
                    })

                except:
                    pass

            # 排序（依保費）
            members = sorted(
                members,
                key=lambda x: int(x["premium"].replace(",", "")),
                reverse=True
            )

            top_html = ""

            rank = 1

            for m in members[:10]:

                top_html += f"""
                <tr>
                    <td>{rank}</td>
                    <td>{m['name']}</td>
                    <td>{m['case']}</td>
                    <td>{m['premium']}</td>
                    <td>{m['fee']}</td>
                </tr>
                """

                rank += 1

            html = f"""

            <!DOCTYPE html>

            <html>

            <head>

            <meta charset="utf-8">

            <style>

            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap');

            body {{
                width:1080px;
                height:1920px;
                margin:0;
                background:
                linear-gradient(180deg,#07143c,#102b72);

                color:white;

                font-family:'Noto Sans TC',sans-serif;

                padding:40px;
                box-sizing:border-box;
            }}

            .title {{
                font-size:90px;
                font-weight:900;
                text-align:center;

                background:linear-gradient(#ffe9a8,#ffbf00);

                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;

                margin-top:20px;
            }}

            .sub {{
                text-align:center;
                font-size:36px;
                margin-top:20px;
                margin-bottom:40px;
            }}

            .card {{
                background:rgba(255,255,255,0.08);

                border:2px solid #ffcc00;

                border-radius:30px;

                padding:30px;

                margin-bottom:40px;
            }}

            .card-title {{
                font-size:50px;
                font-weight:bold;
                color:#ffd54f;

                margin-bottom:20px;
            }}

            table {{
                width:100%;
                border-collapse:collapse;
            }}

            th {{
                font-size:30px;
                padding:20px;
                color:#ffd54f;
                border-bottom:1px solid rgba(255,255,255,0.3);
            }}

            td {{
                text-align:center;
                padding:20px;
                font-size:28px;
                border-bottom:1px solid rgba(255,255,255,0.1);
            }}

            .total {{
                margin-top:30px;

                font-size:40px;

                color:#ffe066;

                line-height:2;
            }}

            .footer {{
                text-align:center;

                margin-top:60px;

                font-size:44px;

                color:#ffd54f;

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

            <div class="card">

                <div class="card-title">
                TOP10 單位績效
                </div>

                <table>

                    <tr>
                        <th>排名</th>
                        <th>業務員</th>
                        <th>件數</th>
                        <th>保費</th>
                        <th>代理費</th>
                    </tr>

                    {top_html}

                </table>

                <div class="total">

                全單位合計<br>

                件數：{int(total_case)}<br>

                保費：{int(total_premium):,}<br>

                代理費：{int(total_fee):,}

                </div>

            </div>

            <div class="footer">
            信安雲林・打造未來的自己
            </div>

            </body>

            </html>

            """

            with open("report.html", "w", encoding="utf-8") as f:
                f.write(html)

            page2 = browser.new_page(
                viewport={
                    "width":1080,
                    "height":1920
                }
            )

            page2.goto("file:///app/report.html")

            page2.wait_for_timeout(5000)

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
