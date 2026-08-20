import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score
import joblib

DATASET_PATH = "tkinter_student_performance_dataset_1000.csv"
MODEL_OUTPUT_PATH = "student_performance_model.pkl"

def train():
    df = pd.read_csv(DATASET_PATH)
    print(f"Loaded dataset: {len(df)} records")

    feature_cols = [
        "Attendance Rate (%)",
        "Daily Study Hours",
        "Internal Assessment (%)",
        "Assignment Score (%)",
        "Previous Semester Score (%)"
    ]
    target_col = "Predicted Score (%)"

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f"Model Evaluation -> R² Score: {r2:.4f} | RMSE: {rmse:.4f}")

    joblib.dump(model, MODEL_OUTPUT_PATH)
    print(f"Model serialized and saved to '{MODEL_OUTPUT_PATH}'")

if __name__ == "__main__":
    train()
