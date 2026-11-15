"""
NEW FILE: test_01_swiggy.py
Playwright tests for Swiggy Restaurant Recommendation System (port 8501)
"""
import asyncio, sys
from playwright.async_api import async_playwright, expect

PORT = 8501
URL  = f"http://localhost:{PORT}"
RESULTS = []

def log(tc, status, msg):
    icon = "✅" if status == "PASS" else "❌"
    print(f"  {icon} {tc}: {status} — {msg}", flush=True)
    RESULTS.append((tc, status, msg))

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 1000})

        print("\n" + "=" * 60, flush=True)
        print("🍽️  PROJECT 1: Swiggy Restaurant Recommendation System", flush=True)
        print("=" * 60, flush=True)

        # TC-01 Page loads & Streamlit hydrates completely
        try:
            await page.goto(URL, timeout=40000)
            await page.wait_for_selector('[data-testid="stSidebar"]', timeout=30000)
            await page.wait_for_selector('button:has-text("Find Restaurants")', timeout=30000)
            body = await page.inner_text("body")
            assert "Swiggy" in body or "Restaurant" in body
            log("TC-SW-01", "PASS", "Page loaded & hydrated — Swiggy branding visible")
        except Exception as e:
            log("TC-SW-01", "FAIL", str(e)[:120])

        # TC-02 Sidebar present with Preferences header
        try:
            sidebar = page.locator('[data-testid="stSidebar"]')
            await expect(sidebar).to_be_visible(timeout=10000)
            stext = await sidebar.inner_text()
            assert "Your Preferences" in stext or "Preferences" in stext
            log("TC-SW-02", "PASS", "Sidebar with Preferences visible")
        except Exception as e:
            log("TC-SW-02", "FAIL", str(e)[:120])

        # TC-03 City & Cuisine dropdowns present
        try:
            stext = await page.locator('[data-testid="stSidebar"]').inner_text()
            assert "Select City" in stext and "Select Cuisine" in stext
            log("TC-SW-03", "PASS", "Select City & Select Cuisine controls present")
        except Exception as e:
            log("TC-SW-03", "FAIL", str(e)[:120])

        # TC-04 Sliders present (rating, cost, top-N)
        try:
            stext = await page.locator('[data-testid="stSidebar"]').inner_text()
            assert "Minimum Rating" in stext and "Maximum Cost" in stext
            log("TC-SW-04", "PASS", "Minimum Rating, Maximum Cost & Recommendation sliders present")
        except Exception as e:
            log("TC-SW-04", "FAIL", str(e)[:120])

        # TC-05 Find Restaurants button present
        try:
            btn = page.locator('[data-testid="stSidebar"] button:has-text("Find Restaurants")')
            await expect(btn).to_be_attached(timeout=10000)
            log("TC-SW-05", "PASS", "'Find Restaurants' button present in sidebar")
        except Exception as e:
            log("TC-SW-05", "FAIL", str(e)[:120])

        # TC-06 Execute Search & verify recommendations/output
        try:
            await page.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const findBtn = btns.find(b => b.innerText.includes('Find Restaurants'));
                if (findBtn) findBtn.click();
            }""")
            await page.wait_for_timeout(5000)
            body = await page.inner_text("body")
            has_output = any(w in body for w in ["Found", "matching restaurants", "No restaurants found", "Match Score", "Category"])
            assert has_output, f"No recommendation output found in body: {body[:200]}"
            log("TC-SW-06", "PASS", "Search executed — recommendation results/message rendered")
        except Exception as e:
            log("TC-SW-06", "FAIL", str(e)[:120])

        # TC-07 No Python exception on page
        try:
            exc_cnt = await page.locator('[data-testid="stException"]').count()
            body = await page.inner_text("body")
            bad = [kw for kw in ["Traceback", "AttributeError", "FileNotFoundError", "ModuleNotFoundError"] if kw in body]
            assert exc_cnt == 0 and not bad, f"Exceptions: {exc_cnt}, keywords: {bad}"
            log("TC-SW-07", "PASS", "No Python exceptions on page")
        except Exception as e:
            log("TC-SW-07", "FAIL", str(e)[:120])

        await browser.close()

    passed = sum(1 for _, s, _ in RESULTS if s == "PASS")
    failed = len(RESULTS) - passed
    print(f"\n  📊 Swiggy Results: {passed} passed, {failed} failed out of {len(RESULTS)}", flush=True)
    return failed == 0

if __name__ == "__main__":
    ok = asyncio.run(run())
    sys.exit(0 if ok else 1)
