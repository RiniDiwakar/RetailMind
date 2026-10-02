import json
from pathlib import Path


RULES_FILE = Path(__file__).parent / "rules.json"


def load_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("rules", [])


def rule_matches(rule, profile):
    conditions = rule.get("conditions", {})

    if "segment" in conditions:
        if profile["segment"] != conditions["segment"]:
            return False

    if "risk_level" in conditions:
        if profile["risk_level"] != conditions["risk_level"]:
            return False

    if "min_churn_probability" in conditions:
        if profile["churn_probability"] < conditions["min_churn_probability"]:
            return False

    return True


def get_next_best_action(profile):
    rules = load_rules()

    for rule in rules:
        if rule_matches(rule, profile):
            return {
                "action": rule["action"],
                "priority": rule["priority"],
                "reason": rule["reason"],
                "rule_name": rule["name"]
            }

    return {
        "action": "No Action",
        "priority": "Low",
        "reason": "No configured NBA rule matched this customer.",
        "rule_name": None
    }
