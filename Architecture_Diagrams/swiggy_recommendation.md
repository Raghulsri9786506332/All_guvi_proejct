# Swiggy Recommendation — Architecture

> **Source limitation:** The current project copy has the Streamlit `app.py` and a README. The README-referenced preprocessing, recommender, utility, requirements, data, and encoder files are not present. Solid arrows below show visible or documented intended flow; dashed nodes/arrows are not verifiable from the available implementation.

```mermaid
flowchart TD
    User[User]
    App[Available Streamlit app.py]
    UI[Sidebar preferences<br/>city / cuisine / rating / cost / popularity / top N]
    CityUtils[Missing utils.py<br/>get_unique_cities]
    CuisineUtils[Missing utils.py<br/>get_unique_cuisines]
    Data[Missing restaurant dataset<br/>swiggy.csv]
    Preprocess[Missing src/preprocess.py<br/>cleaning and encoding]
    Cleaned[Expected cleaned_data.csv]
    Encoded[Expected encoded_data.csv]
    Encoder[Expected saved encoder]
    Recommender[Missing src/recommend.py<br/>get_recommendations]
    Similarity[README-described cosine similarity<br/>implementation unavailable]
    Results[App result cards / table / CSV download]

    User --> App
    App --> UI
    App -. import unavailable .-> CityUtils
    App -. import unavailable .-> CuisineUtils
    Data -. described input .-> Preprocess
    Preprocess -. described outputs .-> Cleaned
    Preprocess -. described outputs .-> Encoded
    Preprocess -. described output .-> Encoder
    UI -. expected call .-> Recommender
    Cleaned -. expected input .-> Recommender
    Encoded -. expected input .-> Similarity
    Encoder -. expected transform .-> Similarity
    Recommender -. described method only .-> Similarity
    Recommender -. expected result .-> Results
    Results --> User
```

## What is visible in the available app

- The UI requests city, cuisine, a minimum rating, maximum cost, minimum rating count, and a requested number of recommendations.
- On the button click, it calls `get_recommendations(user_input, top_n)`.
- It displays result cards, optional restaurant links, a table view, and a downloadable CSV.
- The app imports `get_unique_cities()` and `get_unique_cuisines()` from a `utils` module that is missing from this copy.

## What the README describes, but cannot currently be verified

The README describes preprocessing, one-hot encoding, and cosine-similarity ranking using restaurant and user-preference features. The source code implementing that behavior and its input/output artifacts are absent. Restore those files before treating the dotted path as the application's verified runtime architecture.
