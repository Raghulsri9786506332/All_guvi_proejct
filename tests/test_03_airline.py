"""
NEW FILE: test_03_airline.py
Playwright tests for Airline Complaint AI System (port 8513)
Tests:
- Introduction & EDA pages
- Single Review Prediction
- Bulk CSV Prediction
- Exception-free checks
"""
import asyncio, os, sys
from playwright.async_api import async_playwright, expect

PORT = 8513
URL  = f"http://localhost:{PORT}"
SAMPLE_CSV = os.path.abspath(r"c:\Users\raghu\OneDrive\New folder\Guvi Auto code\tests\sample_airline_bulk.csv")
RESULTS = []

def log(tc, status, msg):
    icon = "✅" if status == "PASS" else "❌"
    print(f"  {icon} {tc}: {status} — {msg}", flush=True)
    RESULTS.append((tc, status, msg))

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page    = await browser.new_page(viewport={"width": 1440, "height": 1000})

        print("\n" + "=" * 60, flush=True)
        print("✈️   PROJECT 3: Airline Complaint AI System", flush=True)
        print("=" * 60, flush=True)

        # TC-01 Page loads & AirComplaint AI sidebar visible
        try:
            await page.goto(URL, timeout=30000)
            await page.wait_for_selector("text=AirComplaint AI", timeout=25000)
            log("TC-AI-01", "PASS", "Home page loaded — AirComplaint AI sidebar visible")
        except Exception as e:
            log("TC-AI-01", "FAIL", str(e)[:120])

        # TC-02 Sidebar navigation links present
        try:
            sidebar = page.locator('[data-testid="stSidebar"]')
            await expect(sidebar).to_be_visible(timeout=8000)
            stext = await sidebar.inner_text()
            assert "Introduction" in stext and "EDA Dashboard" in stext and "Prediction" in stext
            log("TC-AI-02", "PASS", "Sidebar navigation links (Introduction, EDA, Prediction) visible")
        except Exception as e:
            log("TC-AI-02", "FAIL", str(e)[:120])

        # TC-03 Navigate to Introduction page
        try:
            await page.goto(f"{URL}/Introduction", timeout=30000)
            await page.wait_for_selector("text=Airline Reviews", timeout=25000)
            log("TC-AI-03", "PASS", "Introduction page rendered KPI cards")
        except Exception as e:
            log("TC-AI-03", "FAIL", str(e)[:120])

        # TC-04 Navigate to EDA Dashboard page
        try:
            await page.goto(f"{URL}/EDA_Dashboard", timeout=30000)
            await page.wait_for_selector("text=EDA Dashboard", timeout=25000)
            await page.wait_for_timeout(4000)
            exc_cnt = await page.locator('[data-testid="stException"]').count()
            assert exc_cnt == 0, f"Found {exc_cnt} exception(s) on EDA Dashboard"
            log("TC-AI-04", "PASS", "EDA Dashboard loaded with no exceptions")
        except Exception as e:
            log("TC-AI-04", "FAIL", str(e)[:120])

        # TC-05 Navigate to Prediction page & verify form renders
        try:
            await page.goto(f"{URL}/Prediction", timeout=30000)
            await page.wait_for_selector("text=Severity & Risk Prediction", timeout=25000)
            await page.wait_for_selector("text=Single Review", timeout=25000)
            log("TC-AI-05", "PASS", "Prediction page loaded — Single Review form rendered")
        except Exception as e:
            log("TC-AI-05", "FAIL", str(e)[:120])

        # TC-06 Single Review Prediction
        try:
            title_box = page.locator('input[aria-label="Review Title"]').first
            await title_box.fill("Terrible flight delay and lost baggage")
            await title_box.press("Tab")

            review_box = page.locator('textarea[aria-label="Review Text"]').first
            await review_box.fill(
                "Flight was delayed by 6 hours with zero communication. "
                "Cabin crew were rude, seats were broken, and my luggage was lost."
            )
            await review_box.press("Tab")
            await page.wait_for_timeout(1000)

            pbtn = page.locator('[data-testid="stBaseButton-primary"]').first
            await pbtn.scroll_into_view_if_needed()
            await pbtn.evaluate("el => el.click()")

            await page.wait_for_selector("text=Confidence:", timeout=25000)
            body = await page.inner_text("body")
            assert "Confidence:" in body and "Probability:" in body, f"Missing prediction output in: {body[-500:]}"
            log("TC-AI-06", "PASS", "Single Prediction succeeded — Severity & Service Risk rendered")
        except Exception as e:
            log("TC-AI-06", "FAIL", f"{type(e).__name__}: {str(e)[:120]}")

        # TC-07 Bulk CSV Prediction
        try:
            # Click the Bulk CSV Prediction tab
            bulk_tab = page.locator('button[data-baseweb="tab"]:has-text("Bulk CSV Prediction")')
            await bulk_tab.click()
            await page.wait_for_timeout(2000)

            # Upload the sample CSV
            file_uploader = page.locator('input[type="file"]')
            await file_uploader.set_input_files(SAMPLE_CSV)
            await page.wait_for_timeout(3000)

            # Verify rows loaded
            await page.wait_for_selector("text=Loaded 3 rows.", timeout=15000)

            # Click Run Bulk Prediction button
            run_bulk_btn = page.locator('button:has-text("Run Bulk Prediction")')
            await run_bulk_btn.scroll_into_view_if_needed()
            await run_bulk_btn.evaluate("el => el.click()")

            # Wait for completion message
            await page.wait_for_selector("text=Predictions complete for 3 reviews.", timeout=30000)

            # Verify download button rendered
            dl_btn = page.locator('button:has-text("Download Predictions CSV"), a:has-text("Download Predictions CSV")')
            await expect(dl_btn).to_be_visible(timeout=10000)

            log("TC-AI-07", "PASS", "Bulk CSV Prediction succeeded — 3/3 predictions generated & CSV downloadable")
        except Exception as e:
            log("TC-AI-07", "FAIL", f"{type(e).__name__}: {str(e)[:120]}")

        # TC-08 Check no Python exceptions across page
        try:
            exc_cnt = await page.locator('[data-testid="stException"]').count()
            body = await page.inner_text("body")
            bad = [kw for kw in ["Traceback", "ModuleNotFoundError", "AttributeError", "Prediction failed"] if kw in body]
            assert exc_cnt == 0 and not bad, f"Exceptions={exc_cnt}, bad={bad}"
            log("TC-AI-08", "PASS", "No Python exceptions on Prediction page")
        except Exception as e:
            log("TC-AI-08", "FAIL", str(e)[:120])

        await browser.close()

    passed = sum(1 for _, s, _ in RESULTS if s == "PASS")
    failed = len(RESULTS) - passed
    print(f"\n  📊 Airline Results: {passed} passed, {failed} failed out of {len(RESULTS)}", flush=True)
    return failed == 0

if __name__ == "__main__":
    ok = asyncio.run(run())
    sys.exit(0 if ok else 1)
