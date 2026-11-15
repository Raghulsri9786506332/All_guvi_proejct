"""
NEW FILE: test_04_client_query.py
Playwright tests for DS Client Query Management System (port 8514)
MySQL DB: host=127.0.0.1, user=raghul, db=client_query_db
"""
import asyncio, sys
import mysql.connector
from playwright.async_api import async_playwright, expect

PORT = 8514
URL  = f"http://localhost:{PORT}"
RESULTS = []

def log(tc, status, msg):
    icon = "✅" if status == "PASS" else "❌"
    print(f"  {icon} {tc}: {status} — {msg}", flush=True)
    RESULTS.append((tc, status, msg))

def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="raghul",
        password="Raghulsri9786@",
        database="client_query_db",
    )

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page    = await browser.new_page(viewport={"width": 1440, "height": 1000})

        print("\n" + "=" * 60, flush=True)
        print("🗄️   PROJECT 4: DS Client Query Management System (LAST)", flush=True)
        print("=" * 60, flush=True)

        # TC-01 MySQL DB connection & tables check
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SHOW TABLES")
            tables = [t[0] for t in cur.fetchall()]
            conn.close()
            assert "users" in tables and "queries" in tables, f"Tables={tables}"
            log("TC-CQ-01", "PASS", f"MySQL DB connected — tables: {tables}")
        except Exception as e:
            log("TC-CQ-01", "FAIL", str(e)[:120])

        # TC-02 App loads & hydrates
        try:
            await page.goto(URL, timeout=30000)
            await page.wait_for_selector("text=Client Query Management System", timeout=25000)
            await page.wait_for_selector("text=Demo users:", timeout=15000)
            log("TC-CQ-02", "PASS", "Page loaded — Client Query Management System visible")
        except Exception as e:
            log("TC-CQ-02", "FAIL", str(e)[:120])

        # TC-03 Login & Register tabs exist
        try:
            body = await page.inner_text("body")
            assert "Login" in body and "Register" in body
            log("TC-CQ-03", "PASS", "Login & Register tabs visible")
        except Exception as e:
            log("TC-CQ-03", "FAIL", str(e)[:120])

        # TC-04 Login as Client (client1@gmail.com / client123)
        try:
            user_input = page.locator('input[type="text"]').first
            await user_input.click()
            await user_input.fill("client1@gmail.com")
            await user_input.press("Tab")

            pass_input = page.locator('input[type="password"]').first
            await pass_input.click()
            await pass_input.fill("client123")
            await pass_input.press("Tab")
            await page.wait_for_timeout(500)

            login_btn = page.locator('[data-testid="stFormSubmitButton"] button').first
            await login_btn.click()

            await page.wait_for_selector("text=Client Query Page", timeout=20000)
            log("TC-CQ-04", "PASS", "Client login succeeded — Client Query Page loaded")
        except Exception as e:
            log("TC-CQ-04", "FAIL", f"{type(e).__name__}: {str(e)[:120]}")

        # TC-05 Submit a test query as Client
        test_heading = "Playwright E2E Test Query"
        try:
            # 0: Email ID (pre-filled), 1: Mobile Number, 2: Query Heading
            text_inputs = page.locator('input[type="text"]')
            mob_input = text_inputs.nth(1)
            await mob_input.click()
            await mob_input.fill("9876543210")
            await mob_input.press("Tab")

            hd_input = text_inputs.nth(2)
            await hd_input.click()
            await hd_input.fill(test_heading)
            await hd_input.press("Tab")

            desc_input = page.locator('textarea').first
            await desc_input.click()
            await desc_input.fill("Automated Playwright verification of MySQL query submission.")
            await desc_input.press("Tab")
            await page.wait_for_timeout(500)

            sub_btn = page.locator('[data-testid="stFormSubmitButton"] button').first
            await sub_btn.click()
            await page.wait_for_timeout(4000)

            # Verify in MySQL DB
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT query_id, status FROM queries WHERE query_heading = %s ORDER BY query_id DESC LIMIT 1", (test_heading,))
            row = cur.fetchone()
            conn.close()
            assert row is not None, "Test query not found in MySQL queries table"
            log("TC-CQ-05", "PASS", f"Client query submitted & persisted in MySQL (query_id={row[0]}, status={row[1]})")
        except Exception as e:
            log("TC-CQ-05", "FAIL", f"{type(e).__name__}: {str(e)[:120]}")

        # TC-06 Logout from Client
        try:
            logout_btn = page.locator('[data-testid="stSidebar"] button:has-text("Logout")').first
            await logout_btn.click()
            await page.wait_for_selector("text=Demo users:", timeout=15000)
            log("TC-CQ-06", "PASS", "Client logout succeeded")
        except Exception as e:
            log("TC-CQ-06", "FAIL", f"{type(e).__name__}: {str(e)[:120]}")

        # TC-07 Login as Support (support1 / support123)
        try:
            user_input = page.locator('input[type="text"]').first
            await user_input.click()
            await user_input.fill("support1")
            await user_input.press("Tab")

            pass_input = page.locator('input[type="password"]').first
            await pass_input.click()
            await pass_input.fill("support123")
            await pass_input.press("Tab")

            # Select Support role in Login form
            role_box = page.locator('[data-testid="stSelectbox"]').first
            await role_box.click()
            await page.wait_for_timeout(500)
            support_opt = page.locator('[data-testid="stSelectboxVirtualDropdown"] li', has_text="Support").first
            await support_opt.click()
            await page.wait_for_timeout(500)

            login_btn = page.locator('[data-testid="stFormSubmitButton"] button').first
            await login_btn.click()

            await page.wait_for_selector("text=Support Dashboard", timeout=20000)
            log("TC-CQ-07", "PASS", "Support login succeeded — Support Dashboard loaded")
        except Exception as e:
            log("TC-CQ-07", "FAIL", f"{type(e).__name__}: {str(e)[:120]}")

        # TC-08 Support Dashboard shows All Queries DataFrame & Close Open Query section
        try:
            await page.wait_for_selector("text=All Queries", timeout=10000)
            df_el = page.locator('[data-testid="stDataFrame"]').first
            await expect(df_el).to_be_visible(timeout=10000)
            body = await page.inner_text("body")
            assert "Close Open Query" in body
            log("TC-CQ-08", "PASS", "Support Dashboard All Queries table & Close Open Query rendered")
        except Exception as e:
            log("TC-CQ-08", "FAIL", f"{type(e).__name__}: {str(e)[:120]}")

        # TC-09 Clean up test query from MySQL so DB stays clean
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM queries WHERE query_heading = %s", (test_heading,))
            deleted = cur.rowcount
            conn.commit()
            conn.close()
            assert deleted >= 1, "Expected >=1 test row deleted"
            log("TC-CQ-09", "PASS", f"Cleaned up {deleted} test query row(s) from MySQL")
        except Exception as e:
            log("TC-CQ-09", "FAIL", str(e)[:120])

        # TC-10 No Python/MySQL exceptions on page
        try:
            exc_cnt = await page.locator('[data-testid="stException"]').count()
            body = await page.inner_text("body")
            bad = [kw for kw in ["Traceback", "mysql.connector.errors", "InterfaceError", "ProgrammingError"] if kw in body]
            assert exc_cnt == 0 and not bad, f"Exceptions={exc_cnt}, bad={bad}"
            log("TC-CQ-10", "PASS", "No Python/MySQL exceptions on page")
        except Exception as e:
            log("TC-CQ-10", "FAIL", str(e)[:120])

        await browser.close()

    passed = sum(1 for _, s, _ in RESULTS if s == "PASS")
    failed = len(RESULTS) - passed
    print(f"\n  📊 Client Query Results: {passed} passed, {failed} failed out of {len(RESULTS)}", flush=True)
    return failed == 0

if __name__ == "__main__":
    ok = asyncio.run(run())
    sys.exit(0 if ok else 1)
