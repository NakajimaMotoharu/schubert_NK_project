import unittest
import pg5964_api_sql_constants_plan as t


class ExactSemanticConstantPlanTest(unittest.TestCase):
    def test_only_private_constant_and_same_condition_value(self):
        before = 'final class Example {\n  void write() {\n    if (s.executeUpdate() != 1) throw failure;\n  }\n}\n'
        old = 'if (s.executeUpdate() != 1)'; new = 'if (s.executeUpdate() != EXPECTED_AFFECTED_ROWS)'; const = 'private static final int EXPECTED_AFFECTED_ROWS = 1;'
        actual = t.declared_source(before, [(old, new, 1)], [const])
        self.assertEqual(before.replace('final class Example {', 'final class Example {\n  '+const+'\n').replace(old, new), actual)
        for count in (0, 2, True):
            with self.assertRaises(ValueError):
                t.declared_source(before, [(old, new, count)], [const])
        with self.assertRaises(ValueError):
            t.declared_source(actual, [(new, old, 1)], [const])


if __name__ == '__main__':
    unittest.main()
