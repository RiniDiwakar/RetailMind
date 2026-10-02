import pandas as pd

from pathlib import Path

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score
)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


# --------------------------------------------------
# Load dataset
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = BASE_DIR / "data" / "processed" / "churn_data.csv"

df = pd.read_csv(DATA_FILE)


# --------------------------------------------------
# Features and target
# --------------------------------------------------
FEATURES = [
    "Recency",
    "Frequency",
    "Monetary",
    "TotalQuantity",
    "AvgOrderValue"
]

X = df[FEATURES]
y = df["Churn"]


# --------------------------------------------------
# Keep test set untouched
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# Define models
# --------------------------------------------------

logistic = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(
        max_iter=1000,
        random_state=42
    ))
])

tree = DecisionTreeClassifier(
    max_depth=5,
    random_state=42
)

random_forest = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


models = {
    "Logistic Regression": logistic,
    "Decision Tree": tree,
    "Random Forest": random_forest
}


# --------------------------------------------------
# 5-Fold Stratified Cross Validation
# --------------------------------------------------
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


print("========== 5-FOLD CROSS VALIDATION ==========")

for name, model in models.items():

    f1_scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring="f1"
    )

    auc_scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring="roc_auc"
    )

    print(f"\n{name}")

    print(
        f"F1 scores : "
        f"{[round(x, 4) for x in f1_scores]}"
    )

    print(
        f"Mean F1   : "
        f"{f1_scores.mean():.4f}"
    )

    print(
        f"ROC-AUC scores : "
        f"{[round(x, 4) for x in auc_scores]}"
    )

    print(
        f"Mean ROC-AUC   : "
        f"{auc_scores.mean():.4f}"
    )