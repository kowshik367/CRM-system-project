"""
Automated Screen Capture Script for CRM Web Application using Chrome DevTools Protocol (CDP).
Captures screenshots of every module, role dashboard, reports, and detail pages.
"""

import subprocess
import time
import requests
import json
import base64
import websocket
import os
import shutil

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"C:\Users\new\AppData\Local\Temp\cdp_crm_screenshots"
OUTPUT_DIR = r"C:\Users\new\OneDrive\Desktop\crm\screenshots"
ARTIFACT_DIR = r"C:\Users\new\.gemini\antigravity\brain\770756ec-387c-4554-96f2-57cd03a22e71\screenshots"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)


class CDPBrowser:
    def __init__(self):
        self.cmd_id = 0
        if os.path.exists(USER_DATA_DIR):
            try:
                shutil.rmtree(USER_DATA_DIR)
            except Exception:
                pass

        self.proc = subprocess.Popen([
            CHROME_PATH,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={USER_DATA_DIR}",
            "--remote-debugging-port=9222",
            "about:blank"
        ])
        time.sleep(2)
        r = requests.put("http://127.0.0.1:9222/json/new?about:blank")
        tab_info = r.json()
        self.ws_url = tab_info["webSocketDebuggerUrl"]
        self.ws = websocket.create_connection(self.ws_url, timeout=20)
        self.send("Page.enable")
        self.send("Runtime.enable")
        self.send("Network.enable")
        self.send("Emulation.setDeviceMetricsOverride", {
            "width": 1366,
            "height": 768,
            "deviceScaleFactor": 1,
            "mobile": False
        })

    def send(self, method, params=None):
        self.cmd_id += 1
        msg = {"id": self.cmd_id, "method": method}
        if params:
            msg["params"] = params
        self.ws.send(json.dumps(msg))
        target_id = self.cmd_id
        while True:
            res = json.loads(self.ws.recv())
            if res.get("id") == target_id:
                return res

    def navigate(self, url, wait_seconds=2):
        self.send("Page.navigate", {"url": url})
        time.sleep(wait_seconds)

    def evaluate(self, expression):
        return self.send("Runtime.evaluate", {"expression": expression, "returnByValue": True})

    def capture_screenshot(self, filename, title=""):
        res = self.send("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
        img_data = base64.b64decode(res["result"]["data"])
        
        path1 = os.path.join(OUTPUT_DIR, filename)
        with open(path1, "wb") as f:
            f.write(img_data)

        path2 = os.path.join(ARTIFACT_DIR, filename)
        with open(path2, "wb") as f:
            f.write(img_data)

        print(f"[Captured] {filename} ({len(img_data):,} bytes) - {title}")
        return path1

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass
        self.proc.terminate()
        self.proc.wait()


def run_capture():
    print("=" * 60)
    print("  Starting Automated Screenshot Capture for CRM Modules...")
    print("=" * 60)

    browser = CDPBrowser()

    try:
        # 1. Login Page
        browser.navigate("http://127.0.0.1:5000/login", wait_seconds=1.5)
        browser.capture_screenshot("01_login_page.png", "Authentication & Login Portal")

        # 2. Perform Login as Admin
        browser.evaluate("""
            document.getElementById('username').value = 'admin';
            document.getElementById('password').value = 'admin123';
            document.querySelector('form').submit();
        """)
        time.sleep(2)

        # 3. Admin Executive Dashboard
        browser.navigate("http://127.0.0.1:5000/dashboard/admin", wait_seconds=2.5)
        browser.capture_screenshot("02_admin_dashboard.png", "Executive Administrator Dashboard")

        # 4. Manager Dashboard
        browser.navigate("http://127.0.0.1:5000/dashboard/manager", wait_seconds=2.5)
        browser.capture_screenshot("03_manager_dashboard.png", "Manager Operations Dashboard")

        # 5. Employee Dashboard
        browser.navigate("http://127.0.0.1:5000/dashboard/employee", wait_seconds=2)
        browser.capture_screenshot("04_employee_dashboard.png", "Employee Sales Dashboard")

        # 6. Customer Support Dashboard
        browser.navigate("http://127.0.0.1:5000/dashboard/support", wait_seconds=2)
        browser.capture_screenshot("05_support_dashboard.png", "Customer Support Hub Dashboard")

        # 7. Module 1: Customers Table Listing
        browser.navigate("http://127.0.0.1:5000/customers", wait_seconds=2)
        browser.capture_screenshot("06_module1_customers_list.png", "Module 1 - Customer Accounts & Filters")

        # 8. Module 1: Customer Profile (360-degree view)
        browser.navigate("http://127.0.0.1:5000/customers/1", wait_seconds=2)
        browser.capture_screenshot("07_module1_customer_profile.png", "Module 1 - Customer 360-Degree Profile")

        # 9. Module 2: Sales History & Deals
        browser.navigate("http://127.0.0.1:5000/sales", wait_seconds=2)
        browser.capture_screenshot("08_module2_sales_transactions.png", "Module 2 - Sales Transactions & Deals")

        # 10. Module 2: Quotations List
        browser.navigate("http://127.0.0.1:5000/quotations", wait_seconds=2)
        browser.capture_screenshot("09_module2_quotations.png", "Module 2 - Commercial Quotations")

        # 11. Module 2: Printable Quotation / Invoice
        browser.navigate("http://127.0.0.1:5000/quotations/1", wait_seconds=2)
        browser.capture_screenshot("10_module2_quotation_printable.png", "Module 2 - Printable Quotation & Invoice")

        # 12. Module 2: Customer Orders
        browser.navigate("http://127.0.0.1:5000/orders", wait_seconds=2)
        browser.capture_screenshot("11_module2_customer_orders.png", "Module 2 - Customer Orders & Fulfillment")

        # 13. Module 3: Customer Support & Complaints Queue
        browser.navigate("http://127.0.0.1:5000/complaints", wait_seconds=2)
        browser.capture_screenshot("12_module3_complaints_queue.png", "Module 3 - Support Ticket Queue")

        # 14. Module 3: Ticket Conversation Thread & Details
        browser.navigate("http://127.0.0.1:5000/complaints/1", wait_seconds=2)
        browser.capture_screenshot("13_module3_complaint_thread.png", "Module 3 - Ticket Timeline & Resolution")

        # 15. Module 4: Report Management (Sales Performance)
        browser.navigate("http://127.0.0.1:5000/reports?report_type=sales_performance", wait_seconds=2.5)
        browser.capture_screenshot("14_module4_sales_report.png", "Module 4 - Sales Performance BI Report")

        # 16. Module 4: Revenue & Settlements Report
        browser.navigate("http://127.0.0.1:5000/reports?report_type=revenue_report", wait_seconds=2.5)
        browser.capture_screenshot("15_module4_revenue_report.png", "Module 4 - Revenue & Settlements Report")

        # 17. Module 5: Customer Follow-ups Timeline
        browser.navigate("http://127.0.0.1:5000/follow-ups", wait_seconds=2)
        browser.capture_screenshot("16_module5_followups_timeline.png", "Module 5 - Follow-up Reminders & Overdue")

        # 18. Module 5: Notification Inbox
        browser.navigate("http://127.0.0.1:5000/notifications", wait_seconds=2)
        browser.capture_screenshot("17_module5_notifications.png", "Module 5 - System Notifications Inbox")

        # 19. Module 5: Customer Feedback & CSAT Ratings
        browser.navigate("http://127.0.0.1:5000/feedback", wait_seconds=2)
        browser.capture_screenshot("18_module5_customer_feedback.png", "Module 5 - Customer CSAT Feedback & Reviews")

        # 20. System: User & Employee Administration
        browser.navigate("http://127.0.0.1:5000/users", wait_seconds=2)
        browser.capture_screenshot("19_user_administration.png", "System - User & Role Administration")

        print("=" * 60)
        print("  All 20 screenshots captured successfully!")
        print("=" * 60)

    finally:
        browser.close()


if __name__ == '__main__':
    run_capture()
