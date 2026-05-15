from flask import Flask
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

BROKER_ID = os.getenv("BROKER_ID")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")

@app.route("/")
def home():
    return "AI 戰報系統正常運行"

@app.route("/report")
def report():

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

            # 登入
            page.locator('input[type="text"]').nth(1).fill(BROKER_ID)
            page.locator('input[type="password"]').fill(BROKER_PASSWORD)

            page.keyboard.press("Enter")

            page.wait_for_timeout(5000)

            # 進入業績頁
            page.goto(
                "https://broker.s338.com.tw/Achievement/AchievementListDetail?SType=1"
            )

            page.wait_for_timeout(5000)

            rows = page.locator("table tbody tr")

            count = rows.count()

            for i in range(count):

                try:

                    tds = rows.nth(i).locator("td")

                    if tds.count() < 10:
                        continue

                    name = tds.nth(0).inner_text().strip()

                    status = tds.nth(2).inner_text().strip()

                    if status != "受理":
                        continue

                    case_count = tds.nth(7).inner_text().strip()
                    premium = tds.nth(8).inner_text().strip()
                    fee = tds.nth(9).inner_text().strip()

                    case_count_num = int(float(case_count.replace(",", "")))
                    premium_num = int(float(premium.replace(",", "")))
                    fee_num = int(float(fee.replace(",", "")))

                    members.append({
                        "name": name,
                        "case": case_count_num,
                        "premium": premium_num,
                        "fee": fee_num
                    })

                    total_case += case_count_num
                    total_premium += premium_num
                    total_fee += fee_num

                except:
                    pass

            browser.close()

        # 排序 TOP10
        members = sorted(
            members,
            key=lambda x: x["fee"],
            reverse=True
        )[:10]

        top_html = ""

        for idx, m in enumerate(members):

            rank = idx + 1

            medal = rank

            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"

            top_html += f"""

            <tr>
                <td>{medal}</td>
                <td>{m['name']}</td>
                <td>{m['case']}</td>
                <td>{m['premium']:,}</td>
                <td>{m['fee']:,}</td>
            </tr>

            """

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

    font-family:'Noto Sans TC',sans-serif;

    background:
    radial-gradient(circle at top,#123b8a,#050b1f);

    color:white;

    overflow:hidden;
}}

.container {{

    padding:40px;
}}

.main-title {{

    text-align:center;

    font-size:120px;

    font-weight:900;

    line-height:1;

    margin-top:20px;

    background:linear-gradient(#fff7c2,#ffbf00);

    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;

    text-shadow:0 0 30px rgba(255,200,0,0.5);
}}

.sub-title {{

    text-align:center;

    font-size:42px;

    margin-top:20px;

    color:#ffffffcc;
}}

.panel {{

    margin-top:50px;

    background:rgba(0,0,0,0.25);

    border:3px solid #ffcc00;

    border-radius:30px;

    overflow:hidden;

    box-shadow:
    0 0 40px rgba(255,200,0,0.2);
}}

.panel-header {{

    background:linear-gradient(90deg,#071b44,#1d4ea5);

    padding:25px;

    font-size:54px;

    font-weight:bold;

    color:#ffd54f;

    text-align:center;
}}

table {{

    width:100%;

    border-collapse:collapse;
}}

th {{

    background:#0b1f4d;

    color:#ffd54f;

    font-size:32px;

    padding:24px;
}}

td {{

    text-align:center;

    padding:24px;

    font-size:30px;

    border-bottom:1px solid rgba(255,255,255,0.08);
}}

tr:nth-child(even) {{

    background:rgba(255,255,255,0.03);
}}

.total-box {{

    margin-top:40px;

    background:rgba(255,204,0,0.08);

    border:2px solid rgba(255,204,0,0.4);

    border-radius:25px;

    padding:35px;

    font-size:42px;

    line-height:2;

    color:#ffe082;
}}

.footer {{

    margin-top:60px;

    text-align:center;

    font-size:54px;

    font-weight:900;

    color:#ffd54f;
}}

.slogan {{

    text-align:center;

    margin-top:20px;

    font-size:32px;

    color:#ffffffcc;
}}

</style>

</head>

<body>

<div class="container">

    <div class="main-title">
    每日單位戰報
    </div>

    <div class="sub-title">
    信安雲林 AI 自動戰報系統
    </div>

    <div class="panel">

        <div class="panel-header">
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

    </div>

    <div class="total-box">

        📌 全單位合計<br>

        件數：{total_case}<br>

        保費：{total_premium:,}<br>

        代理費：{total_fee:,}

    </div>

    <div class="footer">
    信安雲林・打造未來的自己
    </div>

    <div class="slogan">
    團結一心・創造無限可能
    </div>

</div>

</body>

</html>

"""

        return html

    except Exception as e:

        return f"錯誤：{str(e)}"

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )
