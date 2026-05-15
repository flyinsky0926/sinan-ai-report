from flask import Flask, send_file
from playwright.sync_api import sync_playwright
import os
from datetime import datetime

app = Flask(__name__)

BROKER_ID = os.getenv("BROKER_ID")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")

@app.route("/")
def home():
    return "AI 戰報系統正常運行"

@app.route("/run")
def run():

    try:

        data = []

        total_case = 0
        total_premium = 0
        total_fee = 0

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox"]
            )

            page = browser.new_page()

            print("前往登入頁")

            page.goto("https://broker.s338.com.tw/")

            page.wait_for_timeout(3000)

            # 登入
            page.locator('input[type="text"]').nth(1).fill(BROKER_ID)
            page.locator('input[type="password"]').fill(BROKER_PASSWORD)

            page.keyboard.press("Enter")

            page.wait_for_timeout(5000)

            print("登入成功")

            # 業績頁
            page.goto("https://broker.s338.com.tw/Achievement/AchievementListDetail?SType=1")

            page.wait_for_timeout(5000)

            print("開始抓資料")

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

                    case_float = float(case_count.replace(",", ""))
                    premium_float = float(premium.replace(",", ""))
                    fee_float = float(fee.replace(",", ""))

                    data.append({
                        "name": name,
                        "case": int(case_float),
                        "premium": int(premium_float),
                        "fee": int(fee_float)
                    })

                    total_case += case_float
                    total_premium += premium_float
                    total_fee += fee_float

                except:
                    pass

            # 排序 TOP10
            sorted_data = sorted(
                data,
                key=lambda x: x['premium'],
                reverse=True
            )

            table_rows = ""

            for idx, item in enumerate(sorted_data[:10]):

                table_rows += f"""
                <tr>
                    <td>{idx+1}</td>
                    <td>{item['name']}</td>
                    <td>{item['case']}</td>
                    <td>{item['premium']:,}</td>
                    <td>{item['fee']:,}</td>
                </tr>
                """

            # 讀 HTML 模板
            with open("report_template.html", "r", encoding="utf-8") as f:
                html = f.read()

            # 取代資料
            html = html.replace(
                "{{date}}",
                datetime.now().strftime("%Y-%m-%d")
            )

            html = html.replace(
                "{{total_case}}",
                str(int(total_case))
            )

            html = html.replace(
                "{{total_premium}}",
                f"{int(total_premium):,}"
            )

            html = html.replace(
                "{{total_fee}}",
                f"{int(total_fee):,}"
            )

            html = html.replace(
                "{{table_rows}}",
                table_rows
            )

            # 生成 HTML
            with open("battle_report.html", "w", encoding="utf-8") as f:
                f.write(html)

            print("HTML 戰報生成成功")

            # 開啟戰報
            page.goto("file:///app/battle_report.html")

            page.wait_for_timeout(2000)

            # 截圖
            page.screenshot(
                path="battle_report.png",
                full_page=True
            )

            print("戰報圖片生成成功")

            browser.close()

        return """
        <h1>AI 戰報生成成功</h1>
        <a href='/report'>查看戰報圖片</a>
        """

    except Exception as e:

        return f"錯誤：{str(e)}"

@app.route("/report")
def report():

    return send_file(
        "battle_report.png",
        mimetype='image/png'
    )

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )
