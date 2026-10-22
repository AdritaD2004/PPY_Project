import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
df= pd.read_csv('"C:\\Users\\Adrita Deshmukhya\\Downloads\\NFWBS_PUF_2016_data.csv"')
df.head()


# Replace negative survey codes representing non-responses with NaN
# Typically, in this dataset: -1 (Refused), -4 (N/A), etc.
df_clean = df.copy()

# Let's see how many negative values exist across the dataset first
num_negatives = (df_clean < 0).sum().sum()
print(f"Total negative values (potential non-responses/missing codes): {num_negatives}")

# Replace negative values with NaN (excluding PUF_ID or columns where negatives might be valid, though in NFWBS most negatives are non-response)
features_to_check = [col for col in df_clean.columns if col != 'PUF_ID']
for col in features_to_check:
    df_clean[col] = df_clean[col].apply(lambda x: np.nan if x < 0 else x)

# Impute missing values with the median of each column
for col in features_to_check:
    if df_clean[col].isnull().any():
        median_val = df_clean[col].median()
        df_clean[col] = df_clean[col].fillna(median_val if not pd.isna(median_val) else 0)

print("Missing values handled and imputed with median.")

from sklearn.ensemble import IsolationForest

# Detect outliers using Isolation Forest
isof = IsolationForest(contamination=0.02, random_state=42)
outliers = isof.fit_predict(df_clean.drop(columns=['PUF_ID']))

# Filter out outliers
df_no_outliers = df_clean[outliers == 1].copy()
print(f"Original shape: {df_clean.shape}")
print(f"Shape after removing outliers: {df_no_outliers.shape}")

# Identify non-numeric columns
non_numeric_cols = df_no_outliers.select_dtypes(exclude=[np.number]).columns.tolist()
print(f"Non-numeric columns: {non_numeric_cols}")

# One-hot encode any categorical columns
df_encoded = pd.get_dummies(df_no_outliers, columns=non_numeric_cols, drop_first=True)
print(f"Shape after one-hot encoding: {df_encoded.shape}")

# Define target variable based on FWBscore (Median split)
median_fwb = df_encoded['FWBscore'].median()
df_encoded['high_FWB'] = (df_encoded['FWBscore'] > median_fwb).astype(int)

# Drop direct score targets and ID columns to prevent data leakage
X = df_encoded.drop(columns=['PUF_ID', 'FWBscore', 'high_FWB'])
y = df_encoded['high_FWB']

# Train Random Forest to find feature importances
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Get top 15 features
importances = rf.feature_importances_
indices = np.argsort(importances)[::-1]
top_k = 15

plt.figure(figsize=(10, 6))
plt.title("Top 15 Features for Predicting High Financial Well-Being")
plt.bar(range(top_k), importances[indices[:top_k]], align="center")
plt.xticks(range(top_k), X.columns[indices[:top_k]], rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Display feature rank
print("Top Features Selected:")
for i in range(top_k):
    print(f"{i+1}. {X.columns[indices[i]]} ({importances[indices[i]]:.4f})")


# Search for relevant columns in the dataset
income_cols = [col for col in df_encoded.columns if 'INC' in col or 'EARN' in col]
savings_cols = [col for col in df_encoded.columns if 'SAV' in col]
debt_cols = [col for col in df_encoded.columns if 'DEBT' in col or 'OWE' in col]
behavior_cols = [col for col in df_encoded.columns if any(prefix in col for prefix in ['ACT1', 'MANAGE1', 'SAVEHABIT', 'FRUGALITY'])]

print("Income-related columns:", income_cols)
print("Savings-related columns:", savings_cols)
print("Debt-related columns:", debt_cols)
print("Selected Behavior columns:", behavior_cols)

# Creating feature proxies based on NFWBS 2016 schema
df_features = df_encoded.copy()

# 1. Savings Rate / Capacity Proxy (using SAVINGSRANGES: higher is more savings)
df_features['savings_capacity'] = df_features['SAVINGSRANGES']

# 2. Debt-to-Income Proxy
# 'PPINCIMP' represents household income categories (1 to 9). 
# 'DEBT' or related borrowing difficulty/stress indicators such as credit cards or loans (e.g., credit card behavior or debt stress).
# We can approximate debt burden using 'SHOCKS_8' (had a foreclosure/bankruptcy) or 'HHHEAD' / 'HOUSERG' / financial stress indicators.
# Let's create a proxy using financial stress indicators if explicit debt values are categorical.
if 'DEBTOFOTHERS' in df_features.columns:
    df_features['debt_income_ratio_proxy'] = df_features['DEBTOFOTHERS'] / df_features['PPINCIMP'].replace(0, 1)
else:
    # fallback to using generic debt stress variables
    debt_stress_cols = [col for col in ['HB_2', 'CC_behavior', 'PRODMND_1'] if col in df_features.columns]
    if debt_stress_cols:
        df_features['debt_income_ratio_proxy'] = df_features[debt_stress_cols].mean(axis=1) / df_features['PPINCIMP'].replace(0, 1)
    else:
        df_features['debt_income_ratio_proxy'] = df_features['ENDSMEET'] / df_features['PPINCIMP'].replace(0, 1)

# 3. Expense Ratio Proxy (Using ENDSMEET: Difficulty making ends meet / regular expenses)
df_features['expense_ratio_proxy'] = df_features['ENDSMEET'] / df_features['PPINCIMP'].replace(0, 1)

# 4. Investment indicator (using security/investment ownership proxy e.g., retirement/savings accounts 'PROD_2', 'PROD_3')
invest_cols = [col for col in ['PROD_2', 'PROD_3', 'RETIRE'] if col in df_features.columns]
if invest_cols:
    df_features['investment_ratio_proxy'] = df_features[invest_cols].mean(axis=1)
else:
    df_features['investment_ratio_proxy'] = df_features['SAVINGSRANGES'] * 0.5  # safe fallback

# 5. Financial Behavior Index
# Aggregate positive behavioral traits (e.g., keeping track, setting goals, saving regularly)
behavior_features = [col for col in ['MANAGE1_1', 'MANAGE1_2', 'MANAGE1_3', 'MANAGE1_4', 'SAVEHABIT', 'FRUGALITY'] if col in df_features.columns]
df_features['financial_behavior_index'] = df_features[behavior_features].mean(axis=1)

# Display engineered features
display(df_features[['savings_capacity', 'debt_income_ratio_proxy', 'expense_ratio_proxy', 'investment_ratio_proxy', 'financial_behavior_index']].head())


