"""Pure metadata regressions for BUG2365; no Product, SDK, quota or events execution."""
import ast
import copy
from pathlib import Path
import unittest
from pmo_port_report import port_check_labels, validate_port_check_labels


def projection(tests=8, physical=1, four=(69, 3, 1, 20)):
    return dict(schema='PGPT_PORT_PROJECTION_V1', tests=tests, physical=physical,
                fourCounters=dict(zip(('LINE', 'METHOD', 'CLASS', 'BRANCH'), four)), noCodeClasses=[])


class PortCheckLabelsTest(unittest.TestCase):
    def test_measured_shapes_and_static_counts_generate_exact_labels(self):
        for count, physical, four, raw in [(6, 2, (66, 6, 2, 25), 4), (8, 2, (75, 9, 2, 48), 6), (8, 1, (69, 3, 1, 20), 5), (8, 1, (110, 7, 1, 36), 6)]:
            p = projection(count, physical, four)
            labels = port_check_labels(p, raw)
            self.assertEqual(f'{count} XML method bijection/FES0', labels[1])
            self.assertEqual(f'{physical}physical normal jar bytes/CRC/session', labels[5])
            self.assertEqual('four counters' + '/'.join(map(str, four)) + ' miss0', labels[6])
            self.assertEqual(f'static raw{raw} individually nonapplicable', labels[8])
            validate_port_check_labels(p, raw, labels)

    def test_original_six_method_text_is_rejected_for_eight(self):
        p = projection()
        labels = port_check_labels(p, 5)
        labels[1] = '6 XML method bijection/FES0'
        with self.assertRaises(ValueError):
            validate_port_check_labels(p, 5, labels)

    def test_original_two_physical_text_is_rejected_for_one(self):
        p = projection()
        labels = port_check_labels(p, 5)
        labels[5] = '2physical normal jar bytes/CRC/session'
        with self.assertRaises(ValueError):
            validate_port_check_labels(p, 5, labels)

    def test_counter_and_static_description_tampering_are_rejected(self):
        p = projection()
        for index, value in [(6, 'four counters66/6/2/25 miss0'), (8, 'static raw6 individually nonapplicable')]:
            labels = port_check_labels(p, 5)
            labels[index] = value
            with self.assertRaises(ValueError):
                validate_port_check_labels(p, 5, labels)

    def test_invalid_projection_rejected_and_original_data_not_mutated(self):
        p = projection()
        before = copy.deepcopy(p)
        port_check_labels(p, 5)
        self.assertEqual(before, p)
        for key, value in [('tests', 8.0), ('tests', False), ('physical', 0), ('noCodeClasses', [{}]), ('fourCounters', dict(LINE=69, METHOD=3, CLASS=2, BRANCH=20))]:
            bad = copy.deepcopy(p)
            bad[key] = value
            with self.assertRaises(ValueError):
                port_check_labels(bad, 5)
        with self.assertRaises(ValueError):
            port_check_labels(p, -1)

    def test_all_four_checkers_generate_then_validate_without_fixed_count_strings(self):
        base = Path('evidence/01_PT/007_NK-AUT-001/input')
        for name in ['008_auth_jdbc_independent_post.py', '010_admin_prelude_independent_post.py', '012_session_issue_independent_post.py', '015_session_revocation_independent_post.py']:
            tree = ast.parse((base / name).read_text())
            names = [n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
            self.assertEqual(1, names.count('port_check_labels'))
            self.assertEqual(1, names.count('validate_port_check_labels'))
            self.assertFalse(any(isinstance(n, ast.Constant) and isinstance(n.value, str) and (' XML method bijection/FES0' in n.value or 'physical normal jar bytes/CRC/session' in n.value) for n in ast.walk(tree)))


if __name__ == '__main__':
    unittest.main()
