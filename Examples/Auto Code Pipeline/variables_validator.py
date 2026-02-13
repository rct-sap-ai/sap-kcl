from auto_sap.classes.auto_code_classes import VariableExtractor
from auto_sap.classes.chat_classes import OpenAIChat

chat_bot = OpenAIChat(model_name="gpt-5-nano")
validator = VariableExtractor(chat_bot)

variables = [
    {
        "variable": "pain_score",
        "label": "Pain score at follow up",
        "variable_type": "Continuous",
        "timepoints": [0, 4],
    },
    {
        "variable": "response",
        "label": "Treatment response",
        "variable_type": "Binary",
        "timepoints": [4],
    },
]

timepoints = [
    {"value": 0},
    {"value": 4},
]

errors, warnings = validator.validate(variables, timepoints)

print("Error free example:")
print("Errors:", errors)
print("Warnings:", warnings)


variables = [
    {
        "variable": "pain_score",
        "label": "",
        "variable_type": "Continuous",
        "timepoints": [0, 99],
    },
    {
        "variable": "pain_score",
        "label": "Duplicate variable",
        "variable_type": "WrongType",
        "timepoints": ["baseline"],
    },
]

timepoints = [
    {"value": 0},
    {"value": 4},
]

errors, warnings = validator.validate(variables, timepoints)


print("Error full example:")


print("Errors:")
for e in errors:
    print(" -", e)

print("Warnings:")
for w in warnings:
    print(" -", w)

