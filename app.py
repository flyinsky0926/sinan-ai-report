from flask import Flask
from playwright.sync_api import sync_playwright
import os
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

BROKER_ID = os.getenv("BROKER_ID")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")


@app.route("/")
def home():
    return "AI 戰報系統正常運行"


@app.route("/run")
def run():

    try:

        print("🚀 信安雲林 AI 戰報系統啟動")

        yesterday = datetime.now() - timedelta(days=1)

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox"]
            )

            page = browser.new_page()

            print("🔐 前往登入頁")

            page.goto("https://broker.s338.com.tw/")

            page.wait_for_timeout(5000)

            print("⌨️ 輸入帳號密碼")

            page.locator('input[type="text"]').nth(1).fill(BROKER_ID)

            page.locator('input[type="password"]').fill(BROKER_PASSWORD)

            page.keyboard.press("Enter")

            page.wait_for_timeout(8000)

            print("✅ 登入成功")

            page.goto(
                "https://broker.s338.com.tw/Achievement/AchievementListDetail?SType=1"
            )

            page.wait_for_timeout(5000)

            print("📊 業績頁面載入成功")

            if LINE_NOTIFY_TOKEN:

                requests.post(
                    "https://notify-api.line.me/api/notify",
                    headers={
                        "Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"
                    },
                    data={
                        "message": "AI 戰報執行成功"
                    }
                )

            browser.close()

        return "AI 戰報執行成功"

    except Exception as e:

        print("❌ 發生錯誤：", str(e))

        return f"錯誤：{str(e)}"


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(host="0.0.0.0", port=port)
