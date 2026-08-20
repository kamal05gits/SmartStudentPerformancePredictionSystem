def classify_student(score):
    """Convert a predicted score into a performance class and risk level."""
    score = max(0.0, min(100.0, float(score)))
    if score >= 75.0:
        return "High Distinction", "Low Risk"
    if score >= 50.0:
        return "Moderate / Average", "Medium Risk"
    return "Needs Attention", "High Risk"


def generate_recommendation(risk_level, study_hours, attendance, internal_marks,
                            assignment_score=None, previous_score=None):
    """Generate recommendations from the student's weakest available indicators."""
    study_hours = float(study_hours)
    attendance = float(attendance)
    internal_marks = float(internal_marks)
    assignment_score = None if assignment_score is None else float(assignment_score)
    previous_score = None if previous_score is None else float(previous_score)

    issues = []
    if attendance < 75:
        issues.append("improve attendance to at least 75%")
    if study_hours < 3:
        issues.append("increase focused study time to at least 3 hours/day")
    if internal_marks < 50:
        issues.append("strengthen internal-assessment preparation")
    if assignment_score is not None and assignment_score < 60:
        issues.append("complete assignments consistently and review missed work")
    if previous_score is not None and previous_score < 60:
        issues.append("revise foundational topics from the previous semester")

    if not issues:
        if risk_level == "Low Risk":
            return "Maintain the current study routine, attendance and continuous-assessment performance."
        return "Maintain consistency and focus on the subject areas with the lowest marks."

    if risk_level == "High Risk":
        prefix = "Priority actions: "
    elif risk_level == "Medium Risk":
        prefix = "Recommended actions: "
    else:
        prefix = "Continue monitoring; "

    return prefix + "; ".join(issues) + "."
