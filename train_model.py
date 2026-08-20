import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split

DATASET_PATH = "tkinter_student_performance_dataset_1000.csv"
MODEL_SAVE_PATH = "student_model.pkl"

FEATURE_COLS = [
    "Attendance Rate (%)",
    "Daily Study Hours",
    "Internal Assessment (%)",
    "Assignment Score (%)",
    "Previous Semester Score (%)"
]
TARGET_COL = "Predicted Score (%)"


def load_dataset():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)
    required = FEATURE_COLS + [TARGET_COL]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    df = df[required].copy()
    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna()

    # Keep training data inside the application's valid domain.
    df = df[
        (df["Attendance Rate (%)"].between(0, 100)) &
        (df["Daily Study Hours"].between(0, 24)) &
        (df["Internal Assessment (%)"].between(0, 100)) &
        (df["Assignment Score (%)"].between(0, 100)) &
        (df["Previous Semester Score (%)"].between(0, 100)) &
        (df[TARGET_COL].between(0, 100))
    ]
    return df


def train():
    df = load_dataset()
    print(f"Dataset loaded successfully! Valid records: {len(df)}")

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=10,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = np.clip(model.predict(X_test), 0, 100)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Cross-validation gives a more stable estimate than one train/test split.
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_r2 = cross_val_score(model, X, y, cv=cv, scoring="r2", n_jobs=-1)
    cv_mae = -cross_val_score(model, X, y, cv=cv, scoring="neg_mean_absolute_error", n_jobs=-1)

    print("\nModel Evaluation")
    print(f"Hold-out R2   : {r2:.4f}")
    print(f"Hold-out RMSE : {rmse:.4f}")
    print(f"Hold-out MAE  : {mae:.4f}")
    print(f"5-Fold CV R2  : {cv_r2.mean():.4f} (+/- {cv_r2.std():.4f})")
    print(f"5-Fold CV MAE : {cv_mae.mean():.4f}")

    print("\nFeature Importance")
    importance = pd.Series(model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
    for feature, value in importance.items():
        print(f"{feature:<32} {value:.4f}")

    # Keep the saved artifact as the model itself so existing application code remains compatible.
    joblib.dump(model, MODEL_SAVE_PATH)
    print(f"\nModel saved to '{MODEL_SAVE_PATH}'")

    return model


if __name__ == "__main__":
    train()
