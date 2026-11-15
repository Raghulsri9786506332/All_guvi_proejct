# Swiggy Restaurant Recommendation

## What this project is intended to do

The available app is a Streamlit restaurant recommender. It asks for a city, cuisine, minimum rating, maximum cost, minimum rating count, and number of results. It then displays restaurant suggestions, similarity scores, restaurant links, and a CSV download.

The project README describes a cosine-similarity recommender using one-hot encoded city and cuisine values plus numeric preferences.

More guides: [available app](./APP.md), [algorithm described in the README](./ALGORITHM.md), [missing files](./MISSING_FILES.md), and [interview notes](./INTERVIEW.md).

## Current folder contents and limitation

The current workspace copy contains the nested project README and `app.py`, plus compiled `.pyc` cache files. The README refers to `src/preprocess.py`, `src/recommend.py`, `src/utils.py`, a requirements file, datasets, and a saved encoder, but those source/data files were not present in the inspected project folder. The cached bytecode is not a suitable replacement for editable, readable source code.

Because those files are missing, the preprocessing and recommendation functions cannot be explained or run from this copy yet. Add the source modules, input dataset, and dependency manifest from the complete project before following its original setup instructions.

## Available file guide

- `swiggy_recommendation/app.py` — Streamlit interface. It imports `get_recommendations`, `get_unique_cities`, and `get_unique_cuisines`; displays filters; calls the recommender when the user clicks the search button; displays results as cards/table; and offers a CSV download. These imported functions are not defined in the available app file.
- `swiggy_recommendation/README.md` — describes the expected full project structure, data preparation, and recommendation algorithm. Some of those files are missing in the current copy.
- `src/__pycache__/*.pyc` and `__pycache__/*.pyc` — generated Python bytecode caches. These are not source documentation targets and should not be edited.

## Setup

The current copy is incomplete and does not include the referenced requirements file or source modules. Restore those files before attempting the README's `pip install`, preprocessing, or `streamlit run app.py` steps. Once restored, read the project's own README and verify that the expected data and encoder artifacts exist.
