import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from engine import Rule, ForwardChainingEngine
from kb_loader import load_rules
from main import KB_PATH, collect_initial_facts, main

class AdvisorTests(unittest.TestCase):
    def test_all_ten_assignment_rules(self):
        cases = [
            (['budget_high','portable','long_battery'], 'recommend:premium_ultrabook'),
            (['budget_low','office_only','portable'], 'recommend:budget_ultrabook'),
            (['gaming','budget_medium'], 'recommend:midrange_gaming_laptop'),
            (['gaming','budget_high'], 'recommend:high_end_gaming_laptop'),
            (['creative_work','portable'], 'spec:ram_16_plus'),
            (['creative_work','large_screen'], 'spec:display_15_plus_color_accurate'),
            (['travel_often','long_battery'], 'spec:battery_60wh_plus'),
            (['pref_os_macos'], 'spec:macos_required'),
            (['needs_ai_accel'], 'spec:gpu_with_tensor_cores'),
            (['pref_os_linux','office_only'], 'spec:linux_friendly_hw')]
        rules = load_rules(KB_PATH)
        self.assertEqual(len(rules), 10)
        for facts, expected in cases:
            with self.subTest(expected=expected):
                engine = ForwardChainingEngine(rules)
                engine.assert_facts(facts)
                engine.run()
                self.assertEqual(engine.facts - set(facts), {expected})

    def test_missing_antecedent(self):
        e = ForwardChainingEngine([Rule(['a','b'], 'c')])
        e.assert_facts(['a'])
        e.run()
        self.assertEqual(e.trace, [])

    def test_chaining_and_cycle_termination(self):
        e = ForwardChainingEngine([Rule(['b'],'c'), Rule(['a'],'b'), Rule(['c'],'a')])
        e.assert_facts(['a'])
        e.run()
        self.assertEqual(e.facts, {'a','b','c'})
        self.assertEqual(len(e.trace), 2)
        e.run()
        self.assertEqual(len(e.trace), 2)

    def test_priority_and_stable_ties(self):
        e = ForwardChainingEngine([Rule(['a'],'b',0,'low'),
                                  Rule(['a'],'c',5,'first'), Rule(['a'],'d',5,'second')])
        e.assert_facts(['a'])
        e.run()
        self.assertEqual([s['rule'] for s in e.trace], ['first','second','low'])

    def test_duplicate_consequent(self):
        e = ForwardChainingEngine([Rule(['a'],'b'), Rule(['a'],'b')])
        e.assert_facts(['a'])
        e.run()
        self.assertEqual(len(e.trace), 1)

    def test_conclusion_groups(self):
        e = ForwardChainingEngine([])
        e.assert_facts(['a','spec:ram','recommend:laptop'])
        self.assertEqual(e.conclusions(), {'recommendations':['laptop'], 'specs':['ram'], 'other':['a']})

    def test_multiple_results(self):
        e = ForwardChainingEngine(load_rules(KB_PATH))
        e.assert_facts(['budget_high','portable','long_battery','creative_work','travel_often'])
        e.run()
        self.assertEqual(e.conclusions()['recommendations'], ['premium_ultrabook'])
        self.assertEqual(e.conclusions()['specs'], ['battery_60wh_plus','ram_16_plus'])

    def test_input_validation(self):
        answers = ['invalid',' LOW ','any','maybe','yes','n','n','n','y','n','n','n']
        with patch('builtins.input', side_effect=answers), redirect_stdout(io.StringIO()):
            facts = collect_initial_facts()
        self.assertEqual(set(facts), {'budget_low','portable','office_only'})

    def test_cli_recommendation_and_explanation(self):
        answers = ['high','any','y','y','n','n','y','n','n','n']
        output = io.StringIO()
        with patch('builtins.input', side_effect=answers), redirect_stdout(output):
            main()
        self.assertIn('premium_ultrabook', output.getvalue())
        self.assertIn('Premium Ultrabook: IF', output.getvalue())

    def test_cli_no_match(self):
        output = io.StringIO()
        with patch('builtins.input', side_effect=['low','any'] + ['n']*8), redirect_stdout(output):
            main()
        self.assertIn('No laptop category matched', output.getvalue())

if __name__ == '__main__':
    unittest.main()
