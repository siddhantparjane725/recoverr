import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report
)

from xgboost import XGBClassifier


# ============================================================
# LOAD DATASET
# ============================================================

df = pd.read_csv("data/transactions.csv")

print("=" * 60)
print("RecoverR - Model Training")
print("=" * 60)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

df["historical_success_rate"] = (
    df["previous_successful_transactions"]
    /
    df["previous_transactions"].replace(0, 1)
)

df["high_value_transaction"] = (
    df["amount"] > 10000
).astype(int)


# ============================================================
# FEATURES AND TARGET
# ============================================================

features = [
    "amount",
    "payment_method",
    "bank",
    "failure_reason",
    "retry_count",
    "previous_transactions",
    "previous_successful_transactions",
    "risk_score",
    "historical_success_rate",
    "high_value_transaction"
]

target = "recovered"

X = df[features]
y = df[target]


# ============================================================
# TRAIN / VALIDATION / TEST SPLIT
# ============================================================

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp
)

print("\nDataset Split:")
print(f"Train:      {len(X_train)}")
print(f"Validation: {len(X_val)}")
print(f"Test:       {len(X_test)}")


# ============================================================
# COLUMN GROUPS
# ============================================================

numeric_features = [
    "amount",
    "retry_count",
    "previous_transactions",
    "previous_successful_transactions",
    "risk_score",
    "historical_success_rate",
    "high_value_transaction"
]

categorical_features = [
    "payment_method",
    "bank",
    "failure_reason"
]


# ============================================================
# NUMERIC PREPROCESSING
# ============================================================

numeric_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)


# ============================================================
# CATEGORICAL PREPROCESSING
# ============================================================

categorical_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


# ============================================================
# FULL PREPROCESSOR
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            numeric_transformer,
            numeric_features
        ),
        (
            "cat",
            categorical_transformer,
            categorical_features
        )
    ]
)


# ============================================================
# LOGISTIC REGRESSION
# ============================================================

logistic_model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000
            )
        )
    ]
)


print("\nTraining Logistic Regression...")

logistic_model.fit(
    X_train,
    y_train
)


# ============================================================
# LOGISTIC VALIDATION
# ============================================================

logistic_val_predictions = (
    logistic_model.predict(X_val)
)

logistic_val_probabilities = (
    logistic_model.predict_proba(X_val)[:, 1]
)


logistic_results = {
    "accuracy": accuracy_score(
        y_val,
        logistic_val_predictions
    ),

    "precision": precision_score(
        y_val,
        logistic_val_predictions,
        zero_division=0
    ),

    "recall": recall_score(
        y_val,
        logistic_val_predictions,
        zero_division=0
    ),

    "f1": f1_score(
        y_val,
        logistic_val_predictions,
        zero_division=0
    ),

    "roc_auc": roc_auc_score(
        y_val,
        logistic_val_probabilities
    )
}


# ============================================================
# XGBOOST
# ============================================================

xgb_model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            XGBClassifier(
                n_estimators=250,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=42
            )
        )
    ]
)


print("Training XGBoost...")

xgb_model.fit(
    X_train,
    y_train
)


# ============================================================
# XGBOOST VALIDATION
# ============================================================

xgb_val_predictions = (
    xgb_model.predict(X_val)
)

xgb_val_probabilities = (
    xgb_model.predict_proba(X_val)[:, 1]
)


xgb_results = {
    "accuracy": accuracy_score(
        y_val,
        xgb_val_predictions
    ),

    "precision": precision_score(
        y_val,
        xgb_val_predictions,
        zero_division=0
    ),

    "recall": recall_score(
        y_val,
        xgb_val_predictions,
        zero_division=0
    ),

    "f1": f1_score(
        y_val,
        xgb_val_predictions,
        zero_division=0
    ),

    "roc_auc": roc_auc_score(
        y_val,
        xgb_val_probabilities
    )
}


# ============================================================
# COMPARE MODELS
# ============================================================

print("\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)

results_df = pd.DataFrame(
    [
        logistic_results,
        xgb_results
    ],
    index=[
        "Logistic Regression",
        "XGBoost"
    ]
)

print(
    results_df.round(4)
)


# ============================================================
# SELECT BEST MODEL
# ============================================================

if (
    xgb_results["roc_auc"]
    >=
    logistic_results["roc_auc"]
):

    best_model = xgb_model
    best_model_name = "XGBoost"

else:

    best_model = logistic_model
    best_model_name = "Logistic Regression"


print(
    f"\nSelected Model: {best_model_name}"
)


# ============================================================
# VALIDATION PREDICTIONS
# ============================================================

val_predictions = (
    best_model.predict(X_val)
)

val_probabilities = (
    best_model.predict_proba(X_val)[:, 1]
)


# ============================================================
# FINAL HELD-OUT TEST PREDICTIONS
# ============================================================

test_predictions = (
    best_model.predict(X_test)
)

test_probabilities = (
    best_model.predict_proba(X_test)[:, 1]
)


# ============================================================
# FINAL TEST METRICS
# ============================================================

print("\n" + "=" * 60)
print("FINAL HELD-OUT TEST RESULTS")
print("=" * 60)

print(
    "Accuracy:",
    round(
        accuracy_score(
            y_test,
            test_predictions
        ),
        4
    )
)

print(
    "Precision:",
    round(
        precision_score(
            y_test,
            test_predictions,
            zero_division=0
        ),
        4
    )
)

print(
    "Recall:",
    round(
        recall_score(
            y_test,
            test_predictions,
            zero_division=0
        ),
        4
    )
)

print(
    "F1:",
    round(
        f1_score(
            y_test,
            test_predictions,
            zero_division=0
        ),
        4
    )
)

print(
    "ROC-AUC:",
    round(
        roc_auc_score(
            y_test,
            test_probabilities
        ),
        4
    )
)


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        test_predictions,
        zero_division=0
    )
)


# ============================================================
# CREATE VALIDATION RESULTS
# ============================================================

val_results = X_val.copy()


# Preserve original IDs

val_results.insert(
    0,
    "transaction_id",
    df.loc[X_val.index, "transaction_id"].values
)

val_results.insert(
    1,
    "customer_id",
    df.loc[X_val.index, "customer_id"].values
)


# Actual outcome

val_results["actual_recovered"] = (
    y_val.values
)


# Model prediction

val_results["predicted_recovered"] = (
    val_predictions
)


# Probability

val_results["recovery_probability"] = (
    val_probabilities
)


# Expected recovery value

val_results["expected_recovery_value"] = (
    val_results["amount"]
    *
    val_results["recovery_probability"]
)


# ============================================================
# CREATE TEST RESULTS
# ============================================================

test_results = X_test.copy()


# Preserve original IDs

test_results.insert(
    0,
    "transaction_id",
    df.loc[X_test.index, "transaction_id"].values
)

test_results.insert(
    1,
    "customer_id",
    df.loc[X_test.index, "customer_id"].values
)


# Actual outcome

test_results["actual_recovered"] = (
    y_test.values
)


# Model prediction

test_results["predicted_recovered"] = (
    test_predictions
)


# Probability

test_results["recovery_probability"] = (
    test_probabilities
)


# Expected recovery value

test_results["expected_recovery_value"] = (
    test_results["amount"]
    *
    test_results["recovery_probability"]
)


# ============================================================
# SAVE RESULTS
# ============================================================

os.makedirs(
    "evaluation/results",
    exist_ok=True
)


val_results.to_csv(
    "evaluation/results/validation_predictions.csv",
    index=False
)


test_results.to_csv(
    "evaluation/results/test_predictions.csv",
    index=False
)


# ============================================================
# SAVE MODEL
# ============================================================

os.makedirs(
    "backend/ml",
    exist_ok=True
)


joblib.dump(
    best_model,
    "backend/ml/recovery_model.joblib"
)


# ============================================================
# FINAL STATUS
# ============================================================

print("\nModel saved to:")
print(
    "backend/ml/recovery_model.joblib"
)

print("\nValidation predictions saved to:")
print(
    "evaluation/results/validation_predictions.csv"
)

print("\nTest predictions saved to:")
print(
    "evaluation/results/test_predictions.csv"
)

print("\nTraining completed successfully.")