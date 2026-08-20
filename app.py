import tkinter as tk
from tkinter import messagebox, ttk
import joblib
import numpy as np
from ssi import evaluate_classification, generate_recommendation

MODEL_PATH = "student_performance_model.pkl"

try:
    model = joblib.load(MODEL_PATH)
except Exception:
    model = None

root = tk.Tk()
root.title("Student Performance Prediction System")
root.geometry("750x680")
root.configure(bg="#f4f6f9")

# Header
header = tk.Label(root, text="Student Performance Predictor", font=("Helvetica", 18, "bold"), bg="#2b5797", fg="white", pady=12)
header.pack(fill=tk.X)

form_frame = tk.Frame(root, bg="#f4f6f9", padx=25, pady=15)
form_frame.pack(fill=tk.BOTH, expand=True)

fields = [
    ("Student ID:", "entry_id"),
    ("Full Name:", "entry_name"),
    ("Attendance Rate (%):", "entry_att"),
    ("Daily Study Hours:", "entry_study"),
    ("Internal Assessment (%):", "entry_ia"),
    ("Assignment Score (%):", "entry_assg"),
    ("Previous Semester Score (%):", "entry_prev"),
]

entries = {}
for idx, (label_text, key) in enumerate(fields):
    lbl = tk.Label(form_frame, text=label_text, font=("Helvetica", 11), bg="#f4f6f9", anchor="w")
    lbl.grid(row=idx, column=0, sticky="w", pady=6)
    ent = tk.Entry(form_frame, font=("Helvetica", 11), width=35)
    ent.grid(row=idx, column=1, pady=6, padx=10)
    entries[key] = ent

result_frame = tk.LabelFrame(root, text="Prediction Summary", font=("Helvetica", 12, "bold"), bg="#ffffff", padx=15, pady=10)
result_frame.pack(fill=tk.BOTH, padx=25, pady=10)

lbl_res_score = tk.Label(result_frame, text="Predicted Score: --", font=("Helvetica", 11), bg="#ffffff")
lbl_res_score.pack(anchor="w", pady=2)

lbl_res_class = tk.Label(result_frame, text="Classification / Risk: --", font=("Helvetica", 11), bg="#ffffff")
lbl_res_class.pack(anchor="w", pady=2)

lbl_res_rec = tk.Label(result_frame, text="Recommendation: --", font=("Helvetica", 10, "italic"), fg="#0d6efd", bg="#ffffff", wraplength=650, justify="left")
lbl_res_rec.pack(anchor="w", pady=4)

def run_prediction():
    try:
        att = float(entries["entry_att"].get().strip())
        study = float(entries["entry_study"].get().strip())
        ia = float(entries["entry_ia"].get().strip())
        assg = float(entries["entry_assg"].get().strip())
        prev = float(entries["entry_prev"].get().strip())

        if model:
            features = np.array([[att, study, ia, assg, prev]])
            score = float(model.predict(features)[0])
        else:
            score = (att * 0.20 + study * 1.0 + ia * 0.25 + assg * 0.20 + prev * 0.25)

        classification, risk = evaluate_classification(score)
        rec = generate_recommendation(risk)

        lbl_res_score.config(text=f"Predicted Score: {score:.2f}%")
        lbl_res_class.config(text=f"Classification: {classification}  |  Risk Level: {risk}")
        lbl_res_rec.config(text=f"Recommendation: {rec}")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please ensure all academic fields contain valid numeric inputs.")

btn_predict = tk.Button(root, text="Predict Performance", font=("Helvetica", 12, "bold"), bg="#2b5797", fg="white", padx=15, pady=8, command=run_prediction)
btn_predict.pack(pady=10)

if __name__ == "__main__":
    root.mainloop()
