Module 2: Analytics Pipeline

Now we Read about an end-to-end machine learning workflow on the Titanic dataset, structured across two core phases:
* phases :-> 1
  ** Exploratory Data Analysis
  ** Prediction Modeling 

1. Exploratory Data Analysis (01_eda.py)
* Profiling & Cleaning: Handles missing values via median imputation age, categorical encoding  deck, and row filtering embarked.
* Insights: Analyzes right-skewed fare distributions, IQR outliers, and key bivariate survival drivers across sex, class, and family size.

2. Predictive Modeling (02_modeling.py)
* Leak-Free Preprocessing: Implements stratified train/test splits and fit-on-train transformers (ColumnTransformer).
* Classification & Imbalance: Evaluates Logistic Regression, Decision Tree, and Random Forest models using SMOTE oversampling.
* Regression & Export: Predicts continuous fare values and exports the final end-to-end pipeline via joblib.