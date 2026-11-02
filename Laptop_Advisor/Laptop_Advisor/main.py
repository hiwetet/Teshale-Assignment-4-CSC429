"""Interactive laptop advisor. Run with Python 3.8 or later."""
from pathlib import Path
from kb_loader import load_rules
from engine import ForwardChainingEngine

KB_PATH = Path(__file__).resolve().parent / "kb" / "laptop_rules.json"

def ask_choice(prompt, choices):
    while True:
        answer = input(prompt).strip().lower()
        if answer in choices:
            return answer
        print("Please enter one of: " + ", ".join(choices))

def collect_initial_facts():
    facts = []
    budget = ask_choice("Budget category (low/medium/high): ", ("low", "medium", "high"))
    facts.append("budget_" + budget)
    os_choice = ask_choice("Preferred OS (windows/macos/linux/any): ",
                          ("windows", "macos", "linux", "any"))
    if os_choice != "any":
        facts.append("pref_os_" + os_choice)
    questions = [
        ("portable", "Is portability important?"),
        ("long_battery", "Do you need long battery life?"),
        ("gaming", "Will you use the laptop for gaming?"),
        ("creative_work", "Will you do creative work such as photo or video editing?"),
        ("office_only", "Is your use limited to office work, studying and web browsing?"),
        ("needs_ai_accel", "Do you need hardware acceleration for AI workloads?"),
        ("large_screen", "Do you want a large screen?"),
        ("travel_often", "Do you travel often?")]
    for fact, question in questions:
        if fact == "office_only" and ("gaming" in facts or "creative_work" in facts):
            continue  # Office-only cannot describe gaming or creative use.
        if ask_choice(question + " (y/n): ", ("y", "yes", "n", "no")) in ("y", "yes"):
            facts.append(fact)
    return facts

def main():
    print("Laptop Advisor")
    rules = load_rules(KB_PATH)
    engine = ForwardChainingEngine(rules)
    engine.assert_facts(collect_initial_facts())
    engine.run()
    results = engine.conclusions()
    print("\nRecommendations:")
    for recommendation in results["recommendations"]:
        print("  " + recommendation)
    if not results["recommendations"]:
        print("  No laptop category matched the supplied rules.")
    print("\nSuggested specifications:")
    for spec in results["specs"]:
        print("  " + spec)
    if not results["specs"]:
        print("  No additional specifications matched.")
    print("\nFired rules and explanations:")
    for step in engine.trace:
        print("  {}: IF {} THEN {}".format(step["rule"],
              " AND ".join(step["antecedents"]), step["consequent"]))
    if not engine.trace:
        print("  None.")

if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nSession ended.")
