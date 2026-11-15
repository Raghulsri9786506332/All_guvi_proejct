# Recommendation algorithm described by the Swiggy project

The project's README describes a restaurant recommendation method based on cosine similarity. This section documents the approach described in that README; the source implementation is not present in the current workspace copy, so exact code behavior cannot be confirmed.

## Intended steps

1. Clean restaurant data and handle duplicates, missing values, ratings, review counts, and cost values.
2. Convert categorical fields such as city and cuisine into numerical one-hot features.
3. Combine those features with numeric values such as rating, cost, and rating count.
4. Convert the selected user preferences into a feature vector using the same feature layout.
5. Calculate cosine similarity between that vector and restaurant feature vectors.
6. Return the top-N matches with similarity scores.

Cosine similarity compares the direction of two vectors. A higher score means a restaurant feature vector is more similar to the selected preferences under the chosen encoding. The exact feature scaling and any hard filtering must be checked in the missing recommender module before describing it as implemented behavior.

## Intended preprocessing outputs

The README describes `cleaned_data.csv`, `encoded_data.csv`, and a saved encoder as outputs from a preprocessing script. Those scripts and outputs are not present in the current project folder snapshot.
