# Swiggy Restaurant Recommendation — 100 Interview Questions and Answers

## Scope and evidence

This interview guide is based on the files currently visible in the project: `app.py` and `README.md` under the nested `swiggy_recommendation` directory. The README describes intended preprocessing, one-hot encoding, and cosine-similarity recommendation behavior, but the referenced `src/preprocess.py`, `src/recommend.py`, `src/utils.py`, `requirements.txt`, raw and generated data, and `models/encoder.pkl` are absent from this workspace copy. Therefore, descriptions of those missing components below are explicitly marked as README-described or proposed; their implementation and runtime behavior cannot be verified here. The README's sample counts and results are also claims in documentation, not facts independently confirmed by the missing data.

1. **What does this project aim to do?**  
   **Answer:** The visible app presents itself as a restaurant discovery tool. A user selects a city, cuisine, minimum rating, maximum cost, minimum rating count, and requested number of results. When the user presses **Find Restaurants**, the app passes preference values to a recommendation function and presents returned rows. The app flow is visible, but whether the missing engine actually produces recommendations is not verifiable.

2. **What parts of the project can you inspect in this workspace?**  
   **Answer:** The nested project contains `app.py` and `README.md`, plus a `src` directory with cache files only. The source modules named by the README and imported by the app are not present, nor are the described dependencies, data files, and encoder. This means we can discuss the displayed UI and documented design, but cannot confirm the end-to-end recommender.

3. **Which statements in this guide are implementation facts?**  
   **Answer:** Facts about page setup, controls, function calls, result rendering, and downloads come directly from the visible `app.py`. Algorithm and preprocessing details are described by the README and must be treated as intended design until the missing source is restored and checked. Recommendations about testing, evaluation, and production are proposals, not claims about existing features.

4. **How is the visible interface organized?**  
   **Answer:** It configures a wide Streamlit page, shows a centered Swiggy-themed heading and tagline, loads city and cuisine choices, and puts preference controls in the sidebar. The main panel shows welcome instructions until a search is submitted; afterward, it shows result cards, a CSV download button, and an expandable table when results are available.

5. **How would you explain the user journey in an interview?**  
   **Answer:** First, city and cuisine options are obtained through utility functions. The user adjusts filter controls and presses **Find Restaurants**. The app builds a dictionary of preferences, calls `get_recommendations`, and displays either a no-results warning or ranked restaurant information. It also offers a download and table view. The called utilities and recommender are missing, so only the interface-side sequence is confirmed.

6. **What inputs are passed from the app to the recommender?**  
   **Answer:** The visible dictionary has keys `city`, `cuisine`, `rating`, `rating_count`, and `cost`. The values come from the selected city and cuisine, the minimum-rating slider, the minimum-ratings-count input, and the maximum-cost slider. The app separately passes the selected `top_n` as an argument. How those values are interpreted downstream cannot be verified.

7. **What are the visible city and cuisine controls?**  
   **Answer:** Both are Streamlit select boxes in the sidebar, labeled **Select City** and **Select Cuisine**. Their options come from `get_unique_cities()` and `get_unique_cuisines()`, imported from the absent `utils.py`. The actual lists, sorting, empty-list handling, and whether values match the data cannot be checked in this workspace.

8. **What minimum-rating options does the visible app provide?**  
   **Answer:** The rating slider ranges from 1.0 to 5.0, starts at 3.5, and moves in 0.1 increments. It is sent under the key `rating`. The label says **Minimum Rating**, so the UI implies a threshold, but only the missing recommender can confirm whether it filters rows by that threshold or uses it as a similarity feature.

9. **How does the visible cost control work?**  
   **Answer:** The **Maximum Cost (₹)** slider runs from 50 to 2,000, defaults to 500, and changes by 50. Its selected value is passed under `cost`. The intended meaning is a budget ceiling, but the engine's filtering or scoring behavior is not visible and should be tested after source restoration.

10. **How is popularity represented in the interface?**  
    **Answer:** A number input labeled **Minimum Ratings Count** has a minimum of zero and defaults to 100. Its value is passed as `rating_count`. The app does not set an explicit maximum. Whether the engine treats this strictly as a minimum, handles missing counts, or uses it in similarity is unknown until `recommend.py` is available.

11. **What range does the app allow for the number of recommendations?**  
    **Answer:** The visible slider allows 3 through 100 results and defaults to 10. This differs from the README's sidebar description, which says 3 through 20 with a default of 5. The code is the current UI behavior; the documentation should be updated or checked against the restored implementation.

12. **What happens when the user clicks the search button?**  
    **Answer:** The app constructs the preference dictionary, enters a spinner labeled **Finding restaurants for you...**, and calls `get_recommendations(user_input=user_input, top_n=top_n)`. If the returned DataFrame is empty, it shows a warning. Otherwise, it shows a success message and renders cards. There is no visible exception handling around the recommendation call.

13. **How does the app respond to missing data files?**  
    **Answer:** It wraps the two utility calls for city and cuisine lists in a `try` block that catches `FileNotFoundError`. It then displays a message instructing the user to run `python src/preprocess.py` and calls `st.stop()`. This does not prove that the absent preprocessing script exists or works, and it may not catch other failures such as missing imports or malformed data.

14. **Why may the current app fail before its data-file message appears?**  
    **Answer:** `app.py` imports `get_recommendations` from `recommend` and city/cuisine functions from `utils`, but those modules are absent in the current copy. Python can therefore raise `ModuleNotFoundError` during imports before reaching the `FileNotFoundError` handler. The UI's missing-data message does not cover this missing-code condition.

15. **What does `sys.path.append("src")` do here, and what is a risk?**  
    **Answer:** It adds a path named `src` relative to the process's current working directory so the app can import `recommend` and `utils` as top-level modules. If the app is launched from a different directory, that relative path may not point to the nested project's `src`. A sturdier design derives an absolute project path from `__file__` or packages the source modules and installs the project.

16. **What information is shown before any search?**  
    **Answer:** The landing page welcomes the user and gives five steps: choose a city, choose a cuisine, set rating and budget filters, click **Find Restaurants**, and view recommendations. It also lists cuisine, ratings, budget, city, and similarity-based recommendations as project capabilities. The last capability is a UI/README claim about intended behavior, not proof of a functioning engine.

17. **What does a result card display?**  
    **Answer:** For each returned row, the app displays a rank and restaurant name, then address and cuisine if those columns exist. It also shows a cost category, rating, and cost. A match score appears only when `similarity_score` exists, and a Swiggy link appears only when `link` exists and is not missing.

18. **How are results ranked visually?**  
    **Answer:** The app iterates through the returned DataFrame in its existing row order and numbers rows starting at one. The first three receive medal-style badges; all later rows receive a food badge. The app does not visibly sort the results itself, so ranking order depends on the missing function's output.

19. **How does the app label price bands?**  
    **Answer:** It converts each row's `cost` to a float. Values below 300 are labeled **Budget**; values from 300 up to but not including 700 are **Moderate**; values of 700 or more are **Premium**. These are display categories, not a verified business definition, and invalid or missing costs may cause conversion errors.

20. **How is the match score formatted?**  
    **Answer:** If the row contains `similarity_score`, the app formats it as a percentage with two decimal places. For example, a numeric value of `0.85` is displayed as `85.00%`. This presentation assumes the score is a fraction on a meaningful 0-to-1 scale; the missing recommender must be checked to confirm that assumption.

21. **What conditions control whether the Swiggy link is shown?**  
    **Answer:** The `link` column must exist and its value must satisfy `pd.notna`. The app then renders a Markdown link labeled **View on Swiggy**. It does not visibly validate that the value is a safe, correctly formed URL or that the destination still exists.

22. **What does the success message tell the user?**  
    **Answer:** It reports the number of rows in `results`. A separate information banner repeats the selected city, cuisine, and minimum rating. It does not show the chosen cost or rating-count limits there, although those values are part of the submitted input.

23. **What does the no-results path do?**  
    **Answer:** If `results.empty` is true, the app shows a warning to change filters. It does not show suggestions such as relaxing the budget or rating threshold, nor does it display the table or download control in that branch. Better filter guidance could be a useful proposed UI improvement.

24. **What is included in the CSV download?**  
    **Answer:** The app serializes the full `results` DataFrame with `index=False`, encodes it as UTF-8 bytes, and offers `restaurant_recommendations.csv` with the `text/csv` MIME type. This means the download may contain columns not shown in the cards or table, depending on what the recommender returns.

25. **How is the table view different from the downloaded CSV?**  
    **Answer:** The expandable table selects only columns that both exist and are among `name`, `city`, `cuisine`, `rating`, `cost`, `address`, and `similarity_score`. The CSV contains all result columns. If none of the expected display columns exists, indexing with an empty column list should be explicitly tested.

26. **What does the README say about the recommendation algorithm?**  
    **Answer:** It describes cosine similarity between a user preference vector and restaurant feature vectors, with city and cuisine one-hot encoded. It says recommendations are ordered by similarity and mapped back to cleaned restaurant rows. This is the documented intended algorithm; the implementation is missing and cannot be verified.

27. **How would you explain cosine similarity simply?**  
    **Answer:** Cosine similarity compares the direction of two vectors rather than their raw lengths. It is the dot product divided by the product of the vector lengths. A value closer to one generally means the vectors point in similar directions, but the score's practical meaning depends on the features, scaling, and exact implementation.

28. **What is one-hot encoding, as described by the README?**  
    **Answer:** A category is represented by a set of zero-or-one columns, with one column active for the selected category. For example, city values such as Delhi and Mumbai could become separate indicator columns. The README says city and cuisine are encoded this way; the absent preprocessing code prevents confirming its exact encoder settings or column order.

29. **Why use one-hot encoding for city and cuisine?**  
    **Answer:** It avoids assigning a false numeric order to labels. If Delhi were encoded as 1 and Mumbai as 2, a model might treat Mumbai as “twice” Delhi, which has no sensible categorical meaning. One-hot features represent category membership directly, although a large number of categories can create a wide feature matrix.

30. **What does the README say preprocessing is intended to do?**  
    **Answer:** It describes removing duplicate restaurant entries, replacing `--` ratings with missing values, parsing rating-count strings, removing currency symbols and commas from cost, handling missing values, and one-hot encoding city and cuisine. These are documentation claims. The actual transformations, their order, and their correctness cannot be audited without `preprocess.py`.

31. **How does the README describe rating-count parsing?**  
    **Answer:** It gives an example such as converting `500+ ratings` to 500. A robust implementation would define how to handle commas, text variations, blanks, and invalid values, and would test those cases. The README example alone does not establish how the missing script actually parses them.

32. **How does the README propose handling missing values?**  
    **Answer:** It says rows missing critical fields should be dropped and `rating_count` should be filled with its median. This is an intended policy, not a verified transformation. A restored implementation should document which fields are “critical,” calculate the median on training data when appropriate, and ensure the fill value is applied consistently.

33. **What input and outputs does the README document for preprocessing?**  
    **Answer:** The documented input is `data/swiggy.csv`. The listed outputs are `data/cleaned_data.csv`, `data/encoded_data.csv`, and `models/encoder.pkl`. None of these files or the script is present in this workspace copy, so neither the paths nor the claimed output formats can be validated here.

34. **What dataset columns does the README list?**  
    **Answer:** The schema table lists `id`, `name`, `city`, `rating`, `rating_count`, `cost`, `cuisine`, `lic_no`, `link`, `address`, and `menu`. These are README-documented columns, not columns confirmed from an available CSV. The app visibly relies on some of them, including `name`, `cost`, and `rating`, and conditionally uses address, cuisine, link, and similarity score.

35. **What sample dataset statistics does the README claim?**  
    **Answer:** It claims 60 restaurants across seven cities, more than 20 cuisines, ratings from 4.1 to 4.6, costs from ₹80 to ₹600, and popularity from 80 to 920+ ratings. It also claims 31 encoded columns. Because the dataset and generated outputs are absent, these numbers should be presented as README claims, not independently confirmed results.

36. **What is the README's stated feature-count breakdown?**  
    **Answer:** It says the demo has 31 encoded columns: three numerical features plus 28 one-hot features. The README's described numerical feature set is not fully reconciled with every app preference, and the actual matrix is missing. Restoring the code should verify exact columns and explain which fields affect scores versus acting only as filters.

37. **Why is feature scaling important for this intended cosine approach?**  
    **Answer:** Cosine similarity is sensitive to feature direction, and a numerical feature with a large range can dominate the vector relative to binary category indicators. Scaling numerical values to comparable ranges can reduce that imbalance. The README uses the phrase “Normalize” in its example, but the missing code means the scaling method and whether it is applied are unknown.

38. **What does it mean to encode user preferences consistently with training data?**  
    **Answer:** The user vector must use the same feature names, category vocabulary, and column order as restaurant vectors. A saved encoder is one possible way to preserve that mapping. The README says an encoder is serialized for use by the app, but its artifact and calling code are absent, so consistency has not been demonstrated.

39. **Why can an unseen city or cuisine be a problem?**  
    **Answer:** A category not present when an encoder was fitted may raise an error or produce an all-zero representation, depending on encoder settings. A production-ready implementation should choose and test an explicit unknown-category policy. The README does not state the policy, and the encoder configuration cannot be inspected.

40. **What risks arise when using only cosine similarity for these preferences?**  
    **Answer:** Similarity is not automatically equivalent to user satisfaction. It can reward shared city/cuisine indicators while underweighting or misinterpreting ratings, price, or popularity. It also depends on scaling and feature composition. A restored implementation should test examples and compare rankings with clear business rules or user feedback.

41. **How should strict constraints differ from ranking preferences?**  
    **Answer:** A strict constraint removes ineligible results, such as a restaurant above the maximum budget. A ranking preference influences order, such as preferring a slightly higher rating. The interface labels rating, cost, and rating count as minimum or maximum thresholds, but the missing engine's use of them cannot be confirmed. The design should state which are filters and which are ranking features.

42. **How might a recommendation function use `top_n`?**  
    **Answer:** A typical design would sort eligible restaurants by score and return at most the requested number. The README describes a top-N output, but does not show tie handling, fewer-than-N behavior, or whether filtering happens before truncation. These behaviors should be confirmed and unit-tested in the restored recommender.

43. **Why should a recommender return restaurant details as well as scores?**  
    **Answer:** Scores alone are not useful to a diner. The app needs display fields such as name, rating, cost, and perhaps address and link. The README says encoded indices are mapped back to cleaned data, but the mapping code is missing. A robust design should preserve stable row identifiers and verify that each score is paired with the correct restaurant.

44. **Why is relying on DataFrame row positions risky?**  
    **Answer:** Filtering, sorting, resetting indexes, or reloading data can change row positions. If encoded row number 12 is assumed to match cleaned row number 12 without a stable key, results can be attached to the wrong restaurant. A stable restaurant ID or validated index mapping should be used and tested; the current mapping method is unknown.

45. **What should be checked when reading the serialized encoder?**  
    **Answer:** Verify the artifact exists, can be loaded by the expected library version, and matches the feature schema used to create `encoded_data.csv`. Check the expected column order and categories, and handle corrupted or incompatible artifacts clearly. The README names `models/encoder.pkl`; the file and loading implementation are not present.

46. **Why is loading pickle files a security and compatibility concern?**  
    **Answer:** Pickle can execute code during deserialization, so only trusted artifacts should be loaded. Pickled objects can also break across Python or library versions. In a deployed system, control artifact provenance, pin compatible dependencies, and consider safer, portable formats when possible. This is a general design concern; no pickle-loading code is visible here.

47. **What dependency information is available?**  
    **Answer:** `app.py` visibly imports Streamlit, pandas, and Python's `sys` module. The README instructs users to install from `requirements.txt`, but that file is absent. Dependencies used by the missing modules cannot be inferred with confidence, so the complete environment is unknown.

48. **What should be verified before running the app after restoring the project?**  
    **Answer:** Confirm the source modules, dependency file, raw CSV, preprocessing outputs, and encoder exist; install documented compatible dependencies; and run the preprocessing command from the expected project directory. Then launch Streamlit and test both normal recommendations and known failure cases. The current copy is incomplete and cannot demonstrate a successful run.

49. **Why can the README's quick-start command be misleading in this copy?**  
    **Answer:** It instructs the reader to install requirements and run `python src/preprocess.py`, but the requirements file and preprocessing script are absent here. The README also gives a sample path tied to another user's machine. Treat it as intended setup documentation until paths and files are restored and verified.

50. **What discrepancy exists between the README and the app's top-N control?**  
    **Answer:** The README says the slider is 3–20 with a default of 5, while the visible app sets it to 3–100 with a default of 10. This can confuse users and interviewers. After confirming the intended product behavior, update one source of truth and add a lightweight check or documentation review.

51. **What testing would you add first for the visible app behavior?**  
    **Answer:** Test that the UI creates the expected input dictionary, passes `top_n`, and renders the empty and non-empty paths. Also verify optional columns such as `address`, `cuisine`, `similarity_score`, and `link`, and check the CSV download and table's selected columns. Streamlit interaction tests can use controlled function outputs without requiring production data.

52. **What unit tests would be useful for the documented preprocessing design?**  
    **Answer:** If the missing script is restored, test duplicate removal, `--` ratings, rating-count strings, cost strings with currency symbols and commas, missing critical fields, median filling, and categorical encoding. Include normal values, blanks, malformed text, and boundary cases. These tests are proposed; the current workspace contains no preprocessing implementation to test.

53. **What unit tests would be useful for the intended recommendation engine?**  
    **Answer:** Test that a known city/cuisine preference ranks expected rows, strict constraints exclude ineligible rows if that is the policy, `top_n` caps the output, and ties behave consistently. Verify score bounds and row-to-restaurant mapping. Include unseen categories, empty data, missing values, and zero-length vectors. No such engine is available to run now.

54. **What is a useful integration test for this project?**  
    **Answer:** Starting with a small fixture CSV, run the restored preprocessing flow, load its saved artifacts, submit a known preference through the recommendation function, and confirm the app displays matching restaurant details. This catches mismatches between preprocessing columns, encoder vocabulary, recommender inputs, and UI expectations.

55. **How would you test the missing-data message?**  
    **Answer:** Arrange for the city/cuisine utility lookup to raise `FileNotFoundError`, then assert that the app shows its preprocessing instruction and stops before rendering the controls. Separately test missing imports, malformed data, and corrupt encoders because the current handler catches only `FileNotFoundError` from the utility calls.

56. **How should application errors be handled more clearly?**  
    **Answer:** Distinguish missing source modules, missing files, invalid data, incompatible artifacts, and recommendation failures. Show users an actionable message without hiding the underlying error from logs. The visible app only handles a specific file-not-found condition during option loading and does not wrap `get_recommendations`.

57. **How would you evaluate ranking quality offline?**  
    **Answer:** Use historical interactions or expert judgments to define relevant restaurants for each query, then measure ranking metrics such as Precision@K, Recall@K, and NDCG@K. Split data carefully to avoid leakage and compare against simple baselines such as popular restaurants within the selected city and cuisine. The current project has no visible evaluation code or verified interaction labels.

58. **What does Precision@K measure in a restaurant recommender?**  
    **Answer:** It is the fraction of the top K recommended restaurants that are relevant according to a defined label or judgment. If three of the top five are relevant, Precision@5 is 3/5. It is only meaningful when relevance is defined consistently, for example by held-out clicks, orders, or human ratings.

59. **What does Recall@K measure?**  
    **Answer:** Recall@K is the fraction of all known relevant restaurants that appear in the first K results. It complements precision: a system can have precise top results but fail to retrieve many relevant options. For a small evaluation set, clearly define the relevant pool and account for users who have interacted with only a few restaurants.

60. **Why might NDCG@K be useful?**  
    **Answer:** NDCG rewards relevant results more when they appear near the top and can represent graded relevance, such as a stronger preference for an excellent match than a weak one. That is useful for ranked restaurant lists where order matters. It requires a defensible relevance scale and should be reported alongside simpler metrics.

61. **What baseline would you compare against?**  
    **Answer:** A simple baseline could rank restaurants by rating or popularity after filtering to the chosen city and cuisine. Another could return the most popular eligible restaurants. If cosine similarity does not beat a transparent baseline on offline metrics or user outcomes, the added complexity may not be justified.

62. **How would you avoid data leakage in evaluation?**  
    **Answer:** Keep the evaluation interactions or labels separate from the data used to create rankings and fit preprocessing transformations. Fit encoders and imputers only on training data, then apply those fitted objects to validation or test data. If time affects popularity or availability, use a time-based split so future information does not leak into past recommendations.

63. **Why should the system measure more than recommendation accuracy?**  
    **Answer:** A list can score well on relevance but still be too repetitive, unaffordable, unavailable, or concentrated among a few businesses. Track coverage, diversity, freshness, latency, and constraint violations alongside relevance. The app currently exposes scores and filters but no visible measurement or monitoring system.

64. **What is catalog coverage?**  
    **Answer:** Catalog coverage measures how much of the available restaurant set can be recommended across users or queries. A system that always returns the same few restaurants may have low coverage even if those items perform well. Track it by city, cuisine, and other useful groups to identify underserved parts of the catalog.

65. **What is recommendation diversity, and why might it matter?**  
    **Answer:** Diversity describes how different the items in one list are from one another. A list of nearly identical restaurants may be less useful than one that offers meaningful alternatives while still matching the request. Diversity should not override explicit needs such as city or budget, and its effect should be tested with users.

66. **How could popularity create bias in this recommender?**  
    **Answer:** If rating count or popularity strongly influences the score, established restaurants may dominate while newer or less-reviewed businesses are rarely shown. Conversely, ignoring confidence in low-count ratings can promote noisy options. Evaluate exposure by restaurant and relevant groups, and consider calibrated popularity or exploration policies if evidence supports them.

67. **How would you handle the confidence of a restaurant rating?**  
    **Answer:** A 4.8 rating based on a handful of reviews is less reliable than a similar rating based on many reviews. A proposed approach is to use a confidence-adjusted rating or Bayesian shrinkage toward an overall or local average, while explaining the method. The README does not describe this and the current implementation cannot be checked.

68. **Why might the average rating not be a fair ranking measure?**  
    **Answer:** Ratings can differ by city, cuisine, customer mix, and time, and small sample sizes can produce extreme averages. A raw average may favor restaurants with few ratings or reflect different expectations across groups. Compare calibrated alternatives and validate them with real user outcomes rather than assuming an average is fully comparable.

69. **How could restaurant availability affect recommendations?**  
    **Answer:** A restaurant may be closed, unavailable for delivery, or no longer listed even if its stored features look ideal. A production system should refresh availability and remove stale entries before ranking or link generation. The visible app checks only whether a link value is not missing; it does not verify availability or link health.

70. **What data-quality checks would you add?**  
    **Answer:** Validate required columns, data types, unique identifiers, valid rating and cost ranges, non-negative counts, and non-empty category values. Measure missingness and duplicates and log unexpected categories or parse failures. Reject or quarantine bad records rather than silently producing misleading recommendations.

71. **How would you design a stable data schema for this app?**  
    **Answer:** Define required fields, types, units, null rules, and stable identifiers in one documented schema. For example, define whether `cost` means per person and how currency is represented, and whether `rating_count` can be unknown. Validate incoming CSVs against that schema before preprocessing or recommendation.

72. **What should happen if there are fewer eligible restaurants than requested?**  
    **Answer:** Return all eligible results, clearly show the count, and avoid padding with ineligible restaurants. The app's success message uses the actual result length, so it can display fewer results, but this depends on the missing recommender returning the correct subset. Add tests for fewer-than-`top_n` cases.

73. **How should zero eligible restaurants be handled?**  
    **Answer:** Return an empty DataFrame with a known schema so the app can safely take its warning branch. A helpful enhancement would explain which filters were most restrictive or offer a user-approved way to relax one. The current UI gives a generic warning and the engine's empty-output contract is unknown.

74. **What edge cases exist around empty city or cuisine options?**  
    **Answer:** If either utility returns an empty list, the app still attempts to create a select box without a valid option. It should detect empty choices and show a useful message or disable search. The utilities are missing, so their current behavior and whether this situation is possible are unknown.

75. **What edge cases exist around numeric values?**  
    **Answer:** The cost conversion `float(row["cost"])` can fail for missing or non-numeric data. Rating display can also fail or look confusing with invalid values. Validate data before rendering, define how missing values appear, and test the slider boundaries and zero rating-count threshold.

76. **What is a sensible way to separate application layers?**  
    **Answer:** Keep the Streamlit page responsible for interaction and presentation, a service layer responsible for preference validation and recommendation orchestration, and data/model modules responsible for loading and scoring. The README's proposed `preprocess.py`, `recommend.py`, and `utils.py` suggests such separation, but the modules are absent and no architecture can be confirmed.

77. **How could the recommendation logic be made easier to test?**  
    **Answer:** Put filtering, feature transformation, scoring, sorting, and result mapping in ordinary Python functions that accept data or injected dependencies. Keep Streamlit calls outside those functions. This lets tests exercise ranking with small deterministic DataFrames without launching a web server.

78. **How would you make preprocessing reproducible?**  
    **Answer:** Record the source data version, transformation configuration, dependency versions, feature names, and output artifact metadata. Use deterministic ordering and write outputs atomically. Add checksums or a dataset version identifier so the encoder and encoded rows can be tied to the same cleaned dataset.

79. **What should be versioned together?**  
    **Answer:** Version the preprocessing code, feature schema, encoder or other transformation artifact, and data snapshot or its identifier. A model artifact created from one schema should not silently be used with a different dataset or app version. The README names output artifacts, but this copy has none and contains no versioning scheme.

80. **How can the system detect a stale encoder?**  
    **Answer:** Store metadata such as feature names, category vocabulary, training-data version, library version, and creation time alongside the artifact. On load, compare that metadata with the expected input schema and fail clearly on mismatch. The current workspace has no artifact or loader to inspect.

81. **How would you improve startup time if the dataset grows?**  
    **Answer:** Load and validate data once per app process or use Streamlit's caching for deterministic resource loading, while ensuring cache invalidation when data or artifacts change. Avoid recomputing the full feature matrix for every interaction if it can be safely reused. Whether the current missing modules already cache or recompute is unknown.

82. **What performance concerns arise with cosine similarity at scale?**  
    **Answer:** Comparing every query vector with every restaurant is roughly linear in the number of restaurants times the number of features. This may be fine for a small catalog but costly for very large data. Benchmark realistic sizes first; then consider optimized vector operations, precomputed representations, or approximate-neighbor search if latency requires it.

83. **What does the README's “60 restaurants” example imply, and what does it not prove?**  
    **Answer:** It suggests a small demo catalog where direct comparison against every restaurant could be practical. It does not prove the actual dataset is present, that 60 rows are loaded, or that performance or recommendation quality is good. Those claims must be confirmed against restored data and executable tests.

84. **How could the app make recommendations explainable?**  
    **Answer:** Show simple reasons such as “matches your city and cuisine” or “within your budget,” provided each reason reflects a verified rule. If scores combine several features, expose understandable score contributions or constraints. The current app shows an optional match percentage but no explanation of how it was produced.

85. **How should the app communicate a similarity percentage?**  
    **Answer:** Explain that it is a model score, not a probability that the user will like the restaurant, unless it has been calibrated and validated as a probability. Avoid implying that 90% means nine in ten users will be satisfied. The visible app labels the value “Match Score” and formats it as a percent but gives no definition.

86. **What accessibility improvements would you propose?**  
    **Answer:** Check that controls have clear labels, badges and emojis are not the only way information is communicated, color contrast is sufficient, and keyboard and screen-reader navigation work. Provide meaningful link text and accessible table headings. These are proposed checks; no accessibility testing is visible in the project.

87. **What privacy questions should be asked before collecting more data?**  
    **Answer:** Determine whether city, cuisine choices, clicks, or orders are stored, why they are needed, how long they are kept, and who can access them. Collect only necessary data and provide appropriate notice and deletion controls. The visible app does not show user accounts or tracking, but absence in these two files does not establish the behavior of any deployment.

88. **What production reliability concerns are visible?**  
    **Answer:** The app assumes the recommendation call returns a DataFrame with usable values and does not show a fallback for engine exceptions. It also depends on relative import paths and external files. Production hardening should add startup checks, clear error reporting, structured logs, health checks, and recovery behavior after the missing source and data dependencies are restored.

89. **How would you monitor the deployed recommender?**  
    **Answer:** Track request volume, latency, errors, empty-result rate, filter distributions, score distributions, catalog freshness, and outcome metrics such as clicks or orders where permitted. Monitor these by city and cuisine to spot data gaps or drift. No monitoring is visible in the current app; this is a proposed production improvement.

90. **What is data drift in this context?**  
    **Answer:** Data drift occurs when incoming restaurant attributes or user preferences change from what preprocessing and ranking were designed around. New cuisine labels, cost changes, or rating patterns can make old encoders and assumptions unreliable. Monitor feature distributions and unknown categories, and define when to refresh data or artifacts.

91. **What is the difference between batch and online recommendations here?**  
    **Answer:** Batch processing could periodically clean the catalog and prepare encoded features, while online serving would apply a user's current filters and rank current candidates at request time. The README describes a preprocessing step and an interactive Streamlit app, which suggests this split as an intended shape, but exact execution and caching are not verifiable.

92. **How might you make filters safer and clearer to users?**  
    **Answer:** State units and semantics directly, explain whether the rating is a minimum and cost is a per-person maximum, and show active filter values with results. Validate that the selected city and cuisine are compatible and give guidance when the combination yields no results. The current labels partly convey intent but do not clarify how filtering and ranking interact.

93. **What should a code reviewer verify in the restored recommendation function?**  
    **Answer:** Verify input validation, schema and type assumptions, consistent encoder use, numerical scaling, filtering order, score calculation, tie handling, top-N behavior, and stable mapping back to restaurant rows. Also check empty inputs, unseen categories, null values, and deterministic results. The function itself is absent, so none of these implementation details can currently be reviewed.

94. **What should a code reviewer verify in the restored preprocessing function?**  
    **Answer:** Check that cleaning rules preserve valid records, parsing is robust, duplicates use a justified key, and missing-value handling matches the documented policy. Confirm that encoded columns align with the saved encoder and that outputs are reproducible and written to the documented locations. The README describes these intentions, but the script is not available.

95. **Which README details should be reconciled after code restoration?**  
    **Answer:** Reconcile the top-N range and default with the app, verify all setup paths and commands, confirm that file names and column names match actual outputs, and validate sample statistics and encoded feature counts against the dataset. Remove or qualify any statement that cannot be reproduced.

96. **How would you describe the current project status honestly in an interview?**  
    **Answer:** I can explain a visible Streamlit UI that gathers preferences and is written to call a recommendation engine. The README documents an intended preprocessing and cosine-similarity design. However, the source modules, dependencies, data, and encoder are missing in this copy, so I cannot claim the recommender runs or that its algorithm, scores, or dataset statistics are verified.

97. **What would you do first after receiving the complete project?**  
    **Answer:** Compare the restored files with the README, inspect the preprocessing and recommendation code, and verify data provenance and schema. Install pinned dependencies in an isolated environment, run preprocessing on a known fixture, and execute focused tests before launching the UI. Then confirm that recommendation output and displayed fields agree end to end.

98. **How would you prioritize improvements after basic correctness is established?**  
    **Answer:** First ensure data, schema, and row mapping are correct; then add unit and integration tests. Next establish offline ranking baselines and measure relevance, diversity, and coverage. Only after evidence shows a need should the system add more complex ranking, caching, or serving infrastructure.

99. **What is the most important limitation to disclose when presenting this project?**  
    **Answer:** The workspace copy is incomplete: only the app and README are available, while their imported modules and referenced data and artifacts are missing. The app's UI logic is visible, but the recommendation engine cannot be executed or audited from this copy. Any claim about working cosine similarity must be labeled as documentation-described intent until verified.

100. **What would count as evidence that the recommender works after restoration?**  
     **Answer:** The missing modules and data are present; dependencies install reproducibly; preprocessing produces validated outputs and a compatible encoder; and an end-to-end test runs a known query through ranking and display. Results should satisfy documented constraints, map to the correct restaurants, and have understandable scores. Quality should then be measured against explicit baselines and evaluation data, not inferred from a successful page render alone.
