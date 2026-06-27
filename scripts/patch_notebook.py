import json

with open("preprocessing.ipynb", "r", encoding="utf-8") as f:
    content = f.read()

target = '"notice_period_days": signals.get("notice_period_days"),\\n'
replacement = target + '        "github_activity_score": signals.get("github_activity_score"),\\n        "interview_completion_rate": signals.get("interview_completion_rate"),\\n'

content = content.replace(target, replacement)

with open("preprocessing.ipynb", "w", encoding="utf-8") as f:
    f.write(content)

print("Notebook patched successfully!")
