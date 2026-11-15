"""
NEW FILE: launch_swiggy.py
Wrapper to launch the Swiggy Streamlit app with proper Python path.
DOES NOT MODIFY the original app.py.
"""
import os
import sys

# Ensure swiggy_recommendation directory and src are in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SWIGGY_DIR = os.path.join(BASE_DIR, "swiggy_recommendation", "swiggy_recommendation")
SRC_DIR = os.path.join(SWIGGY_DIR, "src")

for p in [SRC_DIR, SWIGGY_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.chdir(SWIGGY_DIR)

# Now execute the original app.py
original_app = os.path.join(SWIGGY_DIR, "app.py")
with open(original_app, "r", encoding="utf-8") as f:
    code = f.read()

exec(compile(code, original_app, "exec"))
