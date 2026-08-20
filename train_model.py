import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

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

def train():
    df = pd.read_csv(DATASET_PATH)
    print(f"Dataset loaded successfully! Total records: {len(df)}")

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Model Evaluation -> R2 Score: {r2:.4f} | MSE: {mse:.4f}")

    joblib.dump(model, MODEL_SAVE_PATH)
    print(f"Model saved to '{MODEL_SAVE_PATH}'")

if __name__ == "__main__":
    train()
