"""
NEW FILE: run_all_tests.py
Master test runner - runs Playwright tests for all projects sequentially.
Order: Swiggy → Stock Analysis → Airline Complaint AI → DS Client Query (last)
"""
import subprocess
import sys
import time
import os
import signal

PYTHON = sys.executable
BASE = r"c:\Users\raghu\OneDrive\New folder\Guvi Auto code"

PROJECTS = [
    {
        "name": "1. Swiggy Restaurant Recommendation",
        "app": rf"{BASE}\swiggy_recommendation\swiggy_recommendation\app.py",
        "test": rf"{BASE}\tests\test_01_swiggy.py",
        "port": 8501,
        "cwd": rf"{BASE}\swiggy_recommendation\swiggy_recommendation",
    },
    {
        "name": "2. Data-Driven Stock Analysis",
        "app": rf"{BASE}\Data-Driven Stock Analysis\app.py",
        "test": rf"{BASE}\tests\test_02_stock.py",
        "port": 8512,
        "cwd": rf"{BASE}\Data-Driven Stock Analysis",
    },
    {
        "name": "3. Airline Complaint AI",
        "app": rf"{BASE}\airline-complaint-ai\app.py",
        "test": rf"{BASE}\tests\test_03_airline.py",
        "port": 8513,
        "cwd": rf"{BASE}\airline-complaint-ai",
    },
    {
        "name": "4. DS Client Query Management System (LAST)",
        "app": rf"{BASE}\DS_Client-Query-Management-System\Project-01.py",
        "test": rf"{BASE}\tests\test_04_client_query.py",
        "port": 8514,
        "cwd": rf"{BASE}\DS_Client-Query-Management-System",
    },
]


def run_project(project: dict):
    name = project["name"]
    port = project["port"]
    app_path = project["app"]
    test_path = project["test"]
    cwd = project["cwd"]

    print("\n" + "=" * 70, flush=True)
    print(f"🚀 STARTING PROJECT: {name}", flush=True)
    print("=" * 70, flush=True)

    # Start Streamlit app
    print(f"  Starting app on port {port}...", flush=True)
    app_proc = subprocess.Popen(
        [
            PYTHON, "-m", "streamlit", "run", app_path,
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.runOnSave", "false",
        ],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Give Streamlit time to start up
    time.sleep(8)

    if app_proc.poll() is not None:
        out, err = app_proc.communicate()
        print(f"  ❌ App failed to start!\n  STDOUT: {out.decode()}\n  STDERR: {err.decode()}", flush=True)
        return False

    print(f"  ✅ App running (PID {app_proc.pid})", flush=True)

    # Run Playwright tests
    print(f"  Running Playwright tests: {os.path.basename(test_path)}", flush=True)
    result = subprocess.run(
        [PYTHON, "-u", test_path],
        capture_output=False,
        text=True,
    )
    success = result.returncode == 0

    # Stop the app
    print(f"  Stopping app (PID {app_proc.pid})...", flush=True)
    app_proc.terminate()
    try:
        app_proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        app_proc.kill()

    return success


def main():
    os.makedirs(rf"{BASE}\tests", exist_ok=True)
    overall_results = []

    for project in PROJECTS:
        success = run_project(project)
        overall_results.append((project["name"], success))
        time.sleep(3)  # Brief pause between projects

    print("\n" + "=" * 70, flush=True)
    print("📊 OVERALL TEST RESULTS", flush=True)
    print("=" * 70, flush=True)
    for name, ok in overall_results:
        icon = "✅" if ok else "❌"
        print(f"  {icon} {name}", flush=True)

    all_passed = all(ok for _, ok in overall_results)
    print(f"\n{'🎉 ALL PROJECTS PASSED!' if all_passed else '⚠️  Some projects had failures.'}", flush=True)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
