import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import joblib
import os
from ssi import evaluate_classification, generate_recommendation

MODEL_PATH = "student_performance_model.pkl"
MASTER_CSV_FILE = "student_prediction_output.csv"

FEATURE_COLS = [
    "Attendance Rate (%)",
    "Daily Study Hours",
    "Internal Assessment (%)",
    "Assignment Score (%)",
    "Previous Semester Score (%)"
]

try:
    model = joblib.load(MODEL_PATH)
except Exception:
    model = None

root = tk.Tk()
root.title("Student Performance Management System (Batch & Live)")
root.geometry("1100x700")

top_frame = tk.Frame(root, pady=10)
top_frame.pack(fill=tk.X)

def batch_process_csv():
    filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not filepath:
        return

    try:
        df = pd.read_csv(filepath)
        missing = [col for col in FEATURE_COLS if col not in df.columns]
        if missing:
            messagebox.showerror("Error", f"Missing required columns: {missing}")
            return

        if model:
            predictions = model.predict(df[FEATURE_COLS])
        else:
            predictions = (
                df["Attendance Rate (%)"] * 0.20
                + df["Daily Study Hours"] * 1.0
                + df["Internal Assessment (%)"] * 0.25
                + df["Assignment Score (%)"] * 0.20
                + df["Previous Semester Score (%)"] * 0.25
            )

        df["Predicted Score (%)"] = np.round(predictions, 2)
        classes, risks, recs = [], [], []
        for s in df["Predicted Score (%)"]:
            c, r = evaluate_classification(s)
            classes.append(c)
            risks.append(r)
            recs.append(generate_recommendation(r))

        df["Classification"] = classes
        df["Risk Level"] = risks
        df["Actionable Recommendation"] = recs

        if not os.path.exists(MASTER_CSV_FILE):
            df.to_csv(MASTER_CSV_FILE, index=False)
        else:
            df.to_csv(MASTER_CSV_FILE, mode='a', header=False, index=False)

        update_treeview(df)
        messagebox.showinfo("Success", f"Processed {len(df)} records and updated '{MASTER_CSV_FILE}'")

    except Exception as err:
        messagebox.showerror("Error", f"Failed to process CSV: {err}")

btn_load = tk.Button(top_frame, text="Load & Process Batch CSV", font=("Helvetica", 11, "bold"), bg="#198754", fg="white", padx=12, pady=6, command=batch_process_csv)
btn_load.pack(side=tk.LEFT, padx=20)

tree_frame = tk.Frame(root)
tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

cols = ("StudentID", "Name", "Attendance", "StudyHrs", "PredictedScore", "Risk", "Recommendation")
tree = ttk.Treeview(tree_frame, columns=cols, show='headings')

for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=130)

tree.pack(fill=tk.BOTH, expand=True)

def update_treeview(df):
    for item in tree.get_children():
        tree.delete(item)
    for _, row in df.head(100).iterrows():
        tree.insert("", tk.END, values=(
            row.get("Student ID", "N/A"),
            row.get("Full Name", "N/A"),
            row.get("Attendance Rate (%)", "N/A"),
            row.get("Daily Study Hours", "N/A"),
            row.get("Predicted Score (%)", "N/A"),
            row.get("Risk Level", "N/A"),
            row.get("Actionable Recommendation", "N/A")
        ))

if __name__ == "__main__":
    root.mainloop()
