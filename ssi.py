def calculate_performance(attendance, study_hours, internal_assessment, assignment, prev_semester):
    return (
        attendance * 0.20
        + study_hours * 1.00
        + internal_assessment * 0.25
        + assignment * 0.20
        + prev_semester * 0.25
    )

def evaluate_classification(score):
    if score >= 75.0:
        return "High Distinction", "Low Risk"
    elif score >= 50.0:
        return "Moderate / Average", "Medium Risk"
    else:
        return "Needs Attention", "High Risk"

def generate_recommendation(risk_level):
    if risk_level == "Low Risk":
        return "Maintain current study consistency and active participation."
    elif risk_level == "Medium Risk":
        return "Focus on weaker topics, improve internal marks, and add 1-2 study hours daily."
    else:
        return "Immediate academic intervention required: mandatory tutoring and attendance recovery."
