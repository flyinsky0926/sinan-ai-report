from flask import Flask
from playwright.sync_api import sync_playwright
import os
from datetime import datetime, timedelta

app = Flask(__name__)

page.locator('input[type="text"]').nth(1).fill(BROKER_ID)

page.locator('input[type="password"]').fill(BROKER_PASSWORD)

@app.route("/")
def home():
    return "AI 戰報系統正常運行"

@app.route("/run")
def run():

    try:

        print("🚀 信安雲林 AI 戰報系統啟動")

        yesterday = datetime.now() - timedelta(days=1)

        print(f"📅 查詢日期：{yesterday.strftime('%Y-%m-%d')}")

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            page = browser.new_page()

            print("🔐 前往 broker 登入頁")

            page.goto("https://broker.s338.com.tw/")

            page.wait_for_timeout(3000)

            print("⌨️ 輸入帳號密碼")

            page.fill('input[type="text"]', BROKER_ID)

            page.fill('input[type="password"]', BROKER_PASSWORD)

            page.keyboard.press("Enter")

            page.wait_for_timeout(5000)

            print("✅ 登入完成")

            print("🎯 開始進入績效頁面")

            page.goto("https://broker.s338.com.tw/Achievement/AchievementListDetail?SType=1")

            page.wait_for_timeout(5000)

            print("📊 業績頁面載入成功")

            browser.close()

        return "AI 戰報執行成功"

    except Exception as e:

        print("❌ 發生錯誤")
        print(str(e))

        return f"錯誤：{str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
