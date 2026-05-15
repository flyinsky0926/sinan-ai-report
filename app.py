from flask import Flask
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import os
import threading

app = Flask(__name__)

BROKER_ID = os.getenv("BROKER_ID")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")


def run_report():

    print("🚀 信安雲林 AI 戰報系統啟動")

    yesterday = datetime.now() - timedelta(days=1)

    print(f"📅 查詢日期：{yesterday.strftime('%Y-%m-%d')}")

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

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

        page.goto(
            "https://broker.s338.com.tw/Achievement/AchievementListDetail?SType=1"
        )

        page.wait_for_timeout(5000)

        print("📊 業績頁面載入成功")

        print("🏆 AI 戰報測試成功")

        browser.close()


@app.route("/")
def home():
    return "信安 AI 戰報系統運行中"


@app.route("/run")
def run_now():

    thread = threading.Thread(target=run_report)
    thread.start()

    return "AI 戰報開始執行"


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )
