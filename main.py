import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import joblib
import numpy as np
import pandas as pd
import os
from ssi import classify_student, generate_recommendation

MODEL_PATH = "student_model.pkl"
MASTER_CSV_FILE = "student_prediction.csv"

FEATURE_COLS = [
    "Attendance Rate (%)",
    "Daily Study Hours",
    "Internal Assessment (%)",
    "Assignment Score (%)",
    "Previous Semester Score (%)"
]
ALL_COLUMNS = ["Student ID", "Full Name"] + FEATURE_COLS
RECORD_COLUMNS = ALL_COLUMNS + ["Predicted Score (%)", "Classification", "Risk Level", "Actionable Recommendation"]

try:
    model = joblib.load(MODEL_PATH)
except Exception:
    model = None

root = tk.Tk()
root.geometry("1100x780")
root.title("Smart Student Performance Prediction System")
root.resizable(True, True)

def append_to_master_csv(df_to_add):
    if not os.path.exists(MASTER_CSV_FILE):
        df_to_add.to_csv(MASTER_CSV_FILE, mode='w', header=True, index=False)
    else:
        df_to_add.to_csv(MASTER_CSV_FILE, mode='a', header=False, index=False)

def validate_inputs():
    student_id = entry_id.get().strip()
    student_name = entry_name.get().strip()
    attendance = entry_atten.get().strip()
    study_hours = entry_hours.get().strip()
    internal_marks = entry_ia.get().strip()
    assignment = entry_assg.get().strip()
    prev_perf = entry_prev.get().strip()

    if not all([student_id, student_name, attendance, study_hours, internal_marks, assignment, prev_perf]):
        messagebox.showwarning("Incomplete Form", "Please fill in all input fields.")
        return None

    try:
        attendance = float(attendance)
        study_hours = float(study_hours)
        internal_marks = float(internal_marks)
        assignment = float(assignment)
        prev_perf = float(prev_perf)
    except ValueError:
        messagebox.showerror("Invalid Input", "Academic marks and hours must be numerical values.")
        return None

    if not (0 <= attendance <= 100 and 0 <= internal_marks <= 100 and 0 <= assignment <= 100 and 0 <= prev_perf <= 100):
        messagebox.showerror("Range Error", "Percentage values must fall between 0 and 100.")
        return None

    if not (0 <= study_hours <= 24):
        messagebox.showerror("Range Error", "Daily study hours must be between 0 and 24.")
        return None

    return {
        "Student ID": student_id,
        "Full Name": student_name,
        "Attendance Rate (%)": attendance,
        "Daily Study Hours": study_hours,
        "Internal Assessment (%)": internal_marks,
        "Assignment Score (%)": assignment,
        "Previous Semester Score (%)": prev_perf
    }

def predict_single():
    if model is None:
        messagebox.showerror("Error", "Model file not found. Run train_model.py first.")
        return

    data = validate_inputs()
    if data is None:
        return

    features = np.array([[
        data["Attendance Rate (%)"],
        data["Daily Study Hours"],
        data["Internal Assessment (%)"],
        data["Assignment Score (%)"],
        data["Previous Semester Score (%)"]
    ]])

    pred_score = round(float(model.predict(features)[0]), 2)
    classification, risk_level = classify_student(pred_score)
    rec = generate_recommendation(
        risk_level, data["Daily Study Hours"], data["Attendance Rate (%)"], data["Internal Assessment (%)"]
    )

    lbl_pred.config(text=f"Predicted Score: {pred_score}%")
    lbl_class.config(text=f"Classification: {classification}")
    lbl_risk.config(text=f"Risk Level: {risk_level}")
    lbl_rec.config(text=f"Recommendation: {rec}")

    record = dict(data)
    record.update({
        "Predicted Score (%)": pred_score,
        "Classification": classification,
        "Risk Level": risk_level,
        "Actionable Recommendation": rec
    })
    append_to_master_csv(pd.DataFrame([record]))
    messagebox.showinfo("Success", f"Prediction calculated and saved to '{MASTER_CSV_FILE}'.")

def predict_batch_csv():
    if model is None:
        messagebox.showerror("Error", "Model file not loaded.")
        return

    file_path = filedialog.askopenfilename(title="Select CSV Dataset", filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    try:
        df = pd.read_csv(file_path)
        missing = [col for col in FEATURE_COLS if col not in df.columns]
        if missing:
            messagebox.showerror("Column Error", f"Missing required columns:\n{', '.join(missing)}")
            return

        features = df[FEATURE_COLS].values
        preds = model.predict(features)

        df["Predicted Score (%)"] = np.round(preds, 2)
        df["Classification"], df["Risk Level"] = zip(*df["Predicted Score (%)"].apply(classify_student))
        df["Actionable Recommendation"] = df.apply(
            lambda r: generate_recommendation(
                r["Risk Level"], r["Daily Study Hours"], r["Attendance Rate (%)"], r["Internal Assessment (%)"]
            ), axis=1
        )

        save_cols = [c for c in RECORD_COLUMNS if c in df.columns]
        append_to_master_csv(df[save_cols])
        messagebox.showinfo("Success", f"Processed {len(df)} records into '{MASTER_CSV_FILE}'.")
    except Exception as e:
        messagebox.showerror("Processing Failed", str(e))

def clear_fields():
    for entry in [entry_id, entry_name, entry_atten, entry_hours, entry_ia, entry_assg, entry_prev]:
        entry.delete(0, tk.END)
    lbl_pred.config(text="Predicted Score: --")
    lbl_class.config(text="Classification: --")
    lbl_risk.config(text="Risk Level: --")
    lbl_rec.config(text="Recommendation: --")
    entry_id.focus()

# GUI Components
main_frame = tk.Frame(root, padx=25, pady=20)
main_frame.pack(fill="both", expand=True)

tk.Label(main_frame, text="Smart Student Performance Prediction System", font=("Helvetica", 18, "bold")).pack(pady=(0, 15))

form_frame = tk.Frame(main_frame)
form_frame.pack(fill="x", pady=10)

# Student details
f_left = tk.LabelFrame(form_frame, text="Student Details", font=("Helvetica", 11, "bold"), padx=15, pady=10)
f_left.pack(side="left", fill="both", expand=True, padx=(0, 10))

tk.Label(f_left, text="Student ID:").grid(row=0, column=0, sticky="w", pady=4)
entry_id = tk.Entry(f_left, width=22)
entry_id.grid(row=0, column=1, pady=4)

tk.Label(f_left, text="Full Name:").grid(row=1, column=0, sticky="w", pady=4)
entry_name = tk.Entry(f_left, width=22)
entry_name.grid(row=1, column=1, pady=4)

# Academic details
f_right = tk.LabelFrame(form_frame, text="Academic Metrics", font=("Helvetica", 11, "bold"), padx=15, pady=10)
f_right.pack(side="left", fill="both", expand=True, padx=(10, 0))

fields = [
    ("Attendance Rate (%):", "entry_atten"),
    ("Daily Study Hours:", "entry_hours"),
    ("Internal Assessment (%):", "entry_ia"),
    ("Assignment Score (%):", "entry_assg"),
    ("Previous Semester Score (%):", "entry_prev")
]

entries = {}
for i, (label_text, var_name) in enumerate(fields):
    tk.Label(f_right, text=label_text).grid(row=i, column=0, sticky="w", pady=2)
    e = tk.Entry(f_right, width=20)
    e.grid(row=i, column=1, pady=2)
    entries[var_name] = e

entry_atten = entries["entry_atten"]
entry_hours = entries["entry_hours"]
entry_ia = entries["entry_ia"]
entry_assg = entries["entry_assg"]
entry_prev = entries["entry_prev"]

# Button Bar
btn_frame = tk.Frame(main_frame)
btn_frame.pack(pady=15)

tk.Button(btn_frame, text="Predict Entry", command=predict_single, bg="#2b5797", fg="white", width=14, font=("Helvetica", 10, "bold")).pack(side="left", padx=5)
tk.Button(btn_frame, text="Batch Predict CSV", command=predict_batch_csv, bg="#008272", fg="white", width=16, font=("Helvetica", 10, "bold")).pack(side="left", padx=5)
tk.Button(btn_frame, text="Clear", command=clear_fields, width=10).pack(side="left", padx=5)
tk.Button(btn_frame, text="Exit", command=root.destroy, width=10).pack(side="left", padx=5)

# Results Display
res_frame = tk.LabelFrame(main_frame, text="Assessment & Recommendations", font=("Helvetica", 11, "bold"), padx=20, pady=12)
res_frame.pack(fill="x", pady=10)

lbl_pred = tk.Label(res_frame, text="Predicted Score: --", font=("Helvetica", 11, "bold"), anchor="w")
lbl_pred.pack(fill="x", pady=2)
lbl_class = tk.Label(res_frame, text="Classification: --", font=("Helvetica", 10), anchor="w")
lbl_class.pack(fill="x", pady=2)
lbl_risk = tk.Label(res_frame, text="Risk Level: --", font=("Helvetica", 10), anchor="w")
lbl_risk.pack(fill="x", pady=2)
lbl_rec = tk.Label(res_frame, text="Recommendation: --", font=("Helvetica", 10, "italic"), fg="#333", anchor="w", wraplength=950, justify="left")
lbl_rec.pack(fill="x", pady=2)

if __name__ == "__main__":
    root.mainloop()
