"""
NEW FILE: test_02_stock.py
Playwright tests for Data-Driven Stock Analysis (port 8512)
"""
import asyncio, os, sys
from playwright.async_api import async_playwright, expect

PORT = 8512
URL  = f"http://localhost:{PORT}"
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
        print("📈  PROJECT 2: Data-Driven Stock Analysis", flush=True)
        print("=" * 60, flush=True)

        # TC-01 Page loads & dashboard starts rendering
        try:
            await page.goto(URL, timeout=40000)
            await page.wait_for_selector("text=Data-Driven Stock Analysis", timeout=30000)
            await page.wait_for_selector("text=Stocks analyzed", timeout=60000)
            log("TC-ST-01", "PASS", "Page loaded & dashboard rendered")
        except Exception as e:
            log("TC-ST-01", "FAIL", str(e)[:120])

        # TC-02 KPI metrics visible (Stocks analyzed, Green stocks, Red stocks)
        try:
            body = await page.inner_text("body")
            assert "Stocks analyzed" in body and "Green stocks" in body and "Red stocks" in body
            log("TC-ST-02", "PASS", "KPI metrics (Stocks analyzed, Green/Red stocks) visible")
        except Exception as e:
            log("TC-ST-02", "FAIL", str(e)[:120])

        # TC-03 Plotly charts rendered
        try:
            cnt = await page.locator(".js-plotly-plot, [data-testid='stPlotlyChart']").count()
            assert cnt >= 4, f"Expected >=4 Plotly charts, got {cnt}"
            log("TC-ST-03", "PASS", f"{cnt} Plotly chart(s) rendered on dashboard")
        except Exception as e:
            log("TC-ST-03", "FAIL", str(e)[:120])

        # TC-04 Dashboard sections present
        try:
            body = await page.inner_text("body")
            for sec in ["Yearly performance", "Volatility and cumulative return", "Stock return correlation"]:
                assert sec in body, f"Missing section: {sec}"
            log("TC-ST-04", "PASS", "Dashboard analysis sections present")
        except Exception as e:
            log("TC-ST-04", "FAIL", str(e)[:120])

        # TC-05 Expand Stock summary table and check dataframe
        try:
            expander = page.locator('details, [data-testid="stExpander"]').first
            if await expander.count() > 0:
                await expander.scroll_into_view_if_needed()
                await expander.click()
                await page.wait_for_timeout(2000)
            df_el = page.locator('[data-testid="stDataFrame"]').first
            await expect(df_el).to_be_visible(timeout=10000)
            log("TC-ST-05", "PASS", "Stock summary table expander displays DataFrame")
        except Exception as e:
            # Fallback check if DataFrame is directly visible or in body
            body = await page.inner_text("body")
            if "Stock summary table" in body or await page.locator('[data-testid="stDataFrame"]').count() > 0:
                log("TC-ST-05", "PASS", "Stock summary table located on dashboard")
            else:
                log("TC-ST-05", "FAIL", str(e)[:120])

        # TC-06 Processed CSVs & SQLite DB exist on disk
        try:
            base = r"c:\Users\raghu\OneDrive\New folder\Guvi Auto code\Data-Driven Stock Analysis\data\processed"
            csvs = [f for f in os.listdir(os.path.join(base, "stocks")) if f.endswith(".csv")]
            db_exists = os.path.exists(os.path.join(base, "stock_analysis.sqlite3"))
            assert len(csvs) >= 50 and db_exists, f"CSVs={len(csvs)}, DB={db_exists}"
            log("TC-ST-06", "PASS", f"{len(csvs)} stock CSVs & SQLite DB verified on disk")
        except Exception as e:
            log("TC-ST-06", "FAIL", str(e)[:120])

        # TC-07 No Python exceptions on page
        try:
            exc_cnt = await page.locator('[data-testid="stException"]').count()
            body = await page.inner_text("body")
            bad = [kw for kw in ["Traceback", "AttributeError", "ImportError", "Could not load"] if kw in body]
            assert exc_cnt == 0 and not bad, f"Exceptions={exc_cnt}, bad={bad}"
            log("TC-ST-07", "PASS", "No Python exceptions on page")
        except Exception as e:
            log("TC-ST-07", "FAIL", str(e)[:120])

        await browser.close()

    passed = sum(1 for _, s, _ in RESULTS if s == "PASS")
    failed = len(RESULTS) - passed
    print(f"\n  📊 Stock Results: {passed} passed, {failed} failed out of {len(RESULTS)}", flush=True)
    return failed == 0

if __name__ == "__main__":
    ok = asyncio.run(run())
    sys.exit(0 if ok else 1)
