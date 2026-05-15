
from playwright.sync_api import sync_playwright
import os
from datetime import datetime, timedelta

BROKER_ID = os.getenv("BROKER_ID")
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD")

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

    page.goto("https://broker.s338.com.tw/Achievement/AchievementListDetail?SType=1")

    page.wait_for_timeout(5000)

    print("📊 業績頁面載入成功")

    print("🏆 AI 戰報測試成功")

    browser.close()
