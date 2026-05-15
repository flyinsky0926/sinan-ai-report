from flask import Flask
from playwright.sync_api import sync_playwright
import os
from datetime import datetime, timedelta

app = Flask(__name__)

BROKER_ID = os.getenv("BROKER_ID")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")

@app.route("/")
def home():
    return "AI 戰報系統正常運行"

@app.route("/run")
def run():

    report = []

    try:

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

            # 進入業績頁
            page.goto("https://broker.s338.com.tw/Achievement/AchievementListDetail?SType=1")

            page.wait_for_timeout(5000)

            print("開始抓取資料")

            # 抓表格
            rows = page.locator("table tbody tr")

            count = rows.count()

            report.append("📊 信安 AI 戰報\n")

            total_premium = 0
            total_fee = 0
            total_case = 0

            for i in range(count):

                try:

                    name = rows.nth(i).locator("td").nth(0).inner_text().strip()

                    status = rows.nth(i).locator("td").nth(2).inner_text().strip()

                    # 只抓「受理」
                    if status != "受理":
                        continue

                    case_count = rows.nth(i).locator("td").nth(9).inner_text().strip()

                    premium = rows.nth(i).locator("td").nth(10).inner_text().strip()

                    fee = rows.nth(i).locator("td").nth(11).inner_text().strip()

                    report.append(
                        f"{name}\n"
                        f"件數：{case_count}\n"
                        f"保費：{premium}\n"
                        f"代理費：{fee}\n"
                    )

                    total_case += float(case_count.replace(",", ""))
                    total_premium += float(premium.replace(",", ""))
                    total_fee += float(fee.replace(",", ""))

                except:
                    pass

            report.append("========")

            report.append(
                f"\n📌 全單位合計\n"
                f"件數：{total_case}\n"
                f"保費：{int(total_premium):,}\n"
                f"代理費：{int(total_fee):,}"
            )

            browser.close()

        final_report = "\n".join(report)

        print(final_report)

        return f"<pre>{final_report}</pre>"

    except Exception as e:

        return f"錯誤：{str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
