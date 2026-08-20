def classify_student(score):
    if score >= 75.0:
        classification = "High Distinction"
        risk_level = "Low Risk"
    elif score >= 50.0:
        classification = "Moderate / Average"
        risk_level = "Medium Risk"
    else:
        classification = "Needs Attention"
        risk_level = "High Risk"
    return classification, risk_level

def generate_recommendation(risk_level, study_hours, attendance, internal_marks):
    if risk_level == "Low Risk":
        return "Maintain current study consistency and active participation."
    elif risk_level == "Medium Risk":
        return "Focus on weaker topics, improve internal marks, and add 1-2 study hours daily."
    else:
        recs = []
        if attendance < 65:
            recs.append("Mandatory attendance improvement required")
        if study_hours < 3.0:
            recs.append("Increase daily structured study time")
        if internal_marks < 50:
            recs.append("Schedule remedial coaching sessions for internal assessments")
        return "; ".join(recs) if recs else "Urgent faculty intervention and structured daily tutoring required."
