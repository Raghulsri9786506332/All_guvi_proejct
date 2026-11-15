# Missing files: Swiggy Recommendation

The current nested project folder contains `app.py` and `README.md`. The README describes files that are not present in this copy:

- `requirements.txt` — dependency list.
- `src/preprocess.py` — data cleaning and encoding.
- `src/recommend.py` — recommendation functions such as `get_recommendations`.
- `src/utils.py` — helper functions such as `get_unique_cities` and `get_unique_cuisines`.
- `data/swiggy.csv` — expected source restaurant data.
- `data/cleaned_data.csv` and `data/encoded_data.csv` — expected generated datasets.
- `models/encoder.pkl` — expected saved preprocessing encoder.

Without these files, the app's imports cannot be satisfied and preprocessing cannot be run. The `.pyc` cache files are compiled output; they are not a safe or maintainable replacement for the missing source.

To make the project runnable, restore the actual source and data files from the original project, then follow its README and verify that the expected paths and package versions match.
