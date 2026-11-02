"""Generic, deterministic forward chaining over positive string facts."""
from dataclasses import dataclass
from typing import List, Set, Dict, Any

@dataclass
class Rule:
    antecedents: List[str]
    consequent: str
    priority: int = 0
    name: str = ""

class ForwardChainingEngine:
    def __init__(self, rules: List[Rule]):
        self.rules = list(rules)
        self.facts: Set[str] = set()
        self.trace: List[Dict[str, Any]] = []

    def assert_facts(self, initial: List[str]) -> None:
        self.facts.update(initial)

    def can_fire(self, rule: Rule) -> bool:
        return (all(fact in self.facts for fact in rule.antecedents)
                and rule.consequent not in self.facts)

    def run(self) -> None:
        # Stable sort resolves equal priorities in knowledge-base order.
        ordered = sorted(self.rules, key=lambda rule: rule.priority, reverse=True)
        while True:
            rule = next((r for r in ordered if self.can_fire(r)), None)
            if rule is None:
                return
            self.facts.add(rule.consequent)
            self.trace.append({"rule": rule.name,
                               "antecedents": list(rule.antecedents),
                               "consequent": rule.consequent,
                               "priority": rule.priority})

    def conclusions(self) -> Dict[str, List[str]]:
        results = {"recommendations": [], "specs": [], "other": []}
        for fact in sorted(self.facts):
            if fact.startswith("recommend:"):
                results["recommendations"].append(fact.split(":", 1)[1])
            elif fact.startswith("spec:"):
                results["specs"].append(fact.split(":", 1)[1])
            else:
                results["other"].append(fact)
        return results
