# 🍽️ Swiggy Restaurant Recommendation System

A machine learning-powered recommendation system that suggests restaurants based on user preferences using cosine similarity and data preprocessing techniques.

## 📋 Project Overview

This system analyzes Swiggy restaurant data and provides personalized recommendations based on:
- **Location** (City)
- **Cuisine Type** (Biryani, North Indian, South Indian, etc.)
- **Rating Threshold** (1.0 - 5.0 stars)
- **Budget** (Cost per person in ₹)
- **Popularity** (Minimum number of ratings)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

1. **Navigate to project:**
   ```bash
   cd c:\Users\lenovo\swiggy_recommendation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run data preprocessing:**
   ```bash
   python src/preprocess.py
   ```
   This generates:
   - `data/cleaned_data.csv` — Cleaned dataset without duplicates/missing values
   - `data/encoded_data.csv` — One-Hot encoded features for similarity calculations
   - `models/encoder.pkl` — Serialized encoder for Streamlit

4. **Launch the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
swiggy_recommendation/
├── app.py                 # Streamlit web application
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── src/                  # Core modules
│   ├── preprocess.py     # Data cleaning & One-Hot encoding
│   ├── recommend.py      # Cosine similarity recommendation engine
│   └── utils.py          # Utility functions for UI
│
├── data/                 # Data files
│   ├── swiggy.csv           # Raw restaurant data (user-provided)
│   ├── cleaned_data.csv     # Generated: cleaned dataset
│   └── encoded_data.csv     # Generated: encoded features
│
└── models/               # Trained artifacts
    └── encoder.pkl       # Generated: OneHotEncoder
```

## 🔄 System Workflow

### Step 1: Data Preprocessing (`src/preprocess.py`)

**Purpose:** Clean raw data and prepare numerical features

**Operations:**
- ✅ Remove duplicate restaurant entries
- ✅ Clean data quality issues:
  - Replace '--' ratings with NaN
  - Parse rating counts (e.g., "500+ ratings" → 500)
  - Remove ₹ symbol and commas from cost
- ✅ Handle missing values:
  - Drop rows with missing critical fields
  - Fill rating_count with median
- ✅ One-Hot encode categorical features (city, cuisine)

**Input:** `data/swiggy.csv`

**Outputs:**
- `data/cleaned_data.csv` — Original data with cleaning applied, no encoding
- `data/encoded_data.csv` — Numerical-only dataset (31 columns in demo)
- `models/encoder.pkl` — Pickle file to transform user input

**Data Schema:**
| Column | Type | Example |
|--------|------|---------|
| id | int | 1 |
| name | str | "Biryani House" |
| city | str | "Bangalore" |
| rating | float | 4.5 |
| rating_count | float | 500 |
| cost | float | 250 |
| cuisine | str | "Biryani" |
| lic_no | str | "LIC001" |
| link | str | "https://swiggy.com/1" |
| address | str | "HSR Layout" |
| menu | str | "Biryani Menu" |

### Step 2: Recommendation Engine (`src/recommend.py`)

**Algorithm:** Cosine Similarity

**How it works:**
1. Loads preprocessed data and encoder
2. Converts user input (city, cuisine, rating, cost, rating_count) to a feature vector
3. Encodes categorical features using saved OneHotEncoder
4. Calculates cosine similarity: `cos(θ) = (A·B) / (||A|| × ||B||)`
5. Returns top-N most similar restaurants with similarity scores
6. Maps encoded indices back to cleaned_data for user display

**Key Functions:**
```python
load_data()              # Load cleaned_data, encoded_data, encoder
build_user_vector()     # Convert user input to encoded feature vector
get_recommendations()   # Calculate similarities and return top-N
```

**Example Calculation:**
```
User Input: {city: "Bangalore", cuisine: "Biryani", rating: 4.5, cost: 250, rating_count: 300}
                              ↓
            One-Hot Encode + Normalize
                              ↓
            [numerical features] + [city encoding] + [cuisine encoding]
                              ↓
            Cosine Similarity with all 60 restaurants
                              ↓
            Top 5 most similar restaurants (with scores 0.97, 0.95, 0.93...)
```

### Step 3: Streamlit Application (`app.py`)

**Features:**
- 🎨 Beautiful Swiggy-themed UI
- 🔍 Interactive sidebar filters
- 📊 Real-time recommendation display
- ⚡ Card-based and table views
- 🔗 Direct Swiggy links

**Components:**

**Sidebar Input Panel:**
- City selector (dropdown with unique cities)
- Cuisine selector (dropdown with unique cuisines)
- Rating slider (1.0 - 5.0 stars, default 3.5)
- Cost slider (₹50 - ₹2000, default ₹500)
- Min ratings count (number input, default 100)
- Number of recommendations slider (3-20, default 5)
- "Find Restaurants" button

**Main Display Area:**
- Landing page with instructions (no search yet)
- Recommendation cards (after search):
  - Restaurant name & ranking
  - Address and cuisine
  - Rating and cost metrics
  - Match score (%)
  - Swiggy link
- Expandable detailed table

## 💡 How Similarities Are Calculated

The system uses **Cosine Similarity** to measure how "close" each restaurant is to user preferences:

### Feature Encoding Example

```
Original Data:
┌─────────┬────────┬──────────┐
│ rating  │ city   │ cuisine  │
├─────────┼────────┼──────────┤
│ 4.5     │ Mumbai │ Biryani  │
│ 4.2     │ Delhi  │ Chinese  │
└─────────┴────────┴──────────┘

After One-Hot Encoding:
┌─────────┬────────────┬────────────┬─────────────┬─────────────┬────────────┐
│ rating  │ city_Delhi │ city_Mumbai │ cuisine_Biryan │ cuisine_Chinese │
├─────────┼────────────┼────────────┼─────────────┼─────────────┼────────────┤
│ 4.5     │ 0          │ 1          │ 1           │ 0           │
│ 4.2     │ 1          │ 0          │ 0           │ 1           │
└─────────┴────────────┴────────────┴─────────────┴─────────────┴────────────┘

Similarity = Cosine(User Vector, Restaurant Vector)
           = (u1×r1 + u2×r2 + ... + un×rn) / (||u|| × ||r||)
```

## 📊 Sample Data Statistics

The included sample dataset (`data/swiggy.csv`) contains:
- **60 restaurants** across **7 cities**
- **Bangalore, Chennai, Delhi, Mumbai, Hyderabad, Kolkata, Pune**
- **20+ cuisine types**
- **Rating range:** 4.1 - 4.6 stars
- **Cost range:** ₹80 - ₹600 per person
- **Popularity range:** 80 - 920+ ratings

After preprocessing:
- **0 duplicates** removed
- **0 rows dropped** (all data valid)
- **31 encoded columns** (3 numerical + 28 one-hot encoded)








