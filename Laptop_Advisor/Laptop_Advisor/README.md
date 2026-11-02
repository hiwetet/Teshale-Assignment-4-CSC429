# Laptop Advisor

Completed rule-based expert system using Python 3.8+ and the standard library. No packages or API keys are required.

## Run

Extract the ZIP, open a terminal in the Laptop_Advisor folder, and run:

```powershell
python main.py
```

On systems using the python3 command, use `python3 main.py` instead.
Choose a budget, an operating system preference, and answer the usage questions. Invalid responses are re-prompted. The program displays all matching laptop categories, suggested specifications, and the rules that explain them.

## Test

From the same folder:

```powershell
python -m unittest discover -s tests -v
```

## Files

- engine.py: generic forward chaining and inference trace
- kb_loader.py: JSON rule loader from the supplied starter
- kb/laptop_rules.json: all 10 assignment rules
- main.py: interactive questions and explained results
- tests/test_advisor.py: automated verification
- REPORT.md: design, rule explanations, testing, and limitations
- TEST_RESULTS.txt: captured automated test output
- SAMPLE_RUN.txt: captured console demonstration

The knowledge-base path is resolved relative to main.py, so launching the script from another working directory also works. The two uploaded JSON files were identical; the completed project uses one canonical file in kb/.
