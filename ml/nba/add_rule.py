import json
from pathlib import Path


RULES_FILE = Path(__file__).parent / "rules.json"


def add_rule(
    name,
    segment,
    min_churn_probability,
    risk_level,
    action,
    priority,
    reason
):
    with open(RULES_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    rules = data.get("rules", [])

    new_id = max([rule["id"] for rule in rules], default=0) + 1

    new_rule = {
        "id": new_id,
        "name": name,
        "conditions": {
            "segment": segment,
            "min_churn_probability": min_churn_probability,
            "risk_level": risk_level
        },
        "action": action,
        "priority": priority,
        "reason": reason
    }

    rules.append(new_rule)

    with open(RULES_FILE, "w", encoding="utf-8") as file:
        json.dump({"rules": rules}, file, indent=2)

    return new_rule


def get_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("rules", [])


def delete_rule(rule_id):
    with open(RULES_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    rules = data.get("rules", [])

    updated_rules = [rule for rule in rules if rule["id"] != rule_id]

    if len(updated_rules) == len(rules):
        return False

    with open(RULES_FILE, "w", encoding="utf-8") as file:
        json.dump({"rules": updated_rules}, file, indent=2)

    return True
