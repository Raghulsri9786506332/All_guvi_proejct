# Available application: Swiggy Recommendation

## File

The available app is `swiggy_recommendation/app.py` inside the nested Swiggy project folder.

## What the app does

The Streamlit app asks the user to select a city and cuisine, then set a minimum rating, maximum cost, minimum rating count, and number of recommendations. When the user clicks **Find Restaurants**, it calls the recommendation function and displays matches as cards and a table. It also offers a CSV download.

## Important imports

The app expects these functions from other source modules:

- `get_recommendations(user_input, top_n)` from `recommend`.
- `get_unique_cities()` and `get_unique_cuisines()` from `utils`.

Those modules are not included in the current copy, so these functions are not available to inspect or run.

## App execution flow

1. Configure the Streamlit page and show the title.
2. Load the available city and cuisine choices.
3. If expected data files are missing, show an error and stop the app.
4. Collect user preferences from the sidebar.
5. On button click, pass the preferences to the recommender.
6. Show a warning if no restaurants match; otherwise show result cards, links, metrics, and a downloadable CSV.

The visible UI logic is written at module level; `app.py` does not define its own functions or classes.
