# Swiggy Recommendation interview notes

Use simple, accurate answers. The current workspace copy is incomplete, so distinguish what the README describes from what you can demonstrate in the code.

## What is the project?

“It is a Streamlit restaurant recommendation app. The interface lets a user choose location, cuisine, rating, budget, and popularity preferences, then displays restaurant suggestions.”

## What method does the project README describe?

“The README describes one-hot encoding for categorical values and cosine similarity to compare a user's preferences with restaurant features. The recommender source file is missing from this copy, so I would confirm the exact implementation from the complete source before claiming more detail.”

## Did you use SQL or a JOIN?

“The available Swiggy app file does not show SQL or a database join. It calls a recommendation function that is expected to load processed files. I would only claim SQL usage if it is present in the restored source.”

## Did you use functions or OOP?

“The visible Streamlit app uses imported functions such as `get_recommendations`, `get_unique_cities`, and `get_unique_cuisines`. Those functions are described by their imports but their source files are missing here. The app itself does not define custom classes.”

## What must be ready for the app to run?

“The recommendation and utility modules, requirements file, source restaurant data, processed feature files, and saved encoder need to exist. They are referenced by the project README but missing from this copy.”

## What is cosine similarity?

“It measures how similar two vectors are by comparing their direction. A larger cosine similarity generally means the encoded restaurant features are closer to the user's preferences. The result depends on how features are encoded and scaled.”

## What would you improve?

“I would restore and test the missing source modules, validate the input data, make preprocessing and inference use the exact same saved encoder, and add tests for empty results, missing values, and filters.”
