import unittest
import pg6038_remaining_literal_plan as t


class AllRemainingLiteralPlanTest(unittest.TestCase):
    def test_exact_scope_same_value_and_record_header(self):
        self.assertEqual((22, 33), (len(t.RULES), sum(map(len, t.RULES.values()))))
        text = 'public final class Example {\n  void check(int a) { if (a != 3) return; }\n}\n'
        edits, constants = t.declarations(text, [('if (a != 3)', 'if (a != EXPECTED)', ['int EXPECTED = 3'])])
        changed = t.private_source(text, edits, constants)
        self.assertIn('private static final int EXPECTED = 3;', changed)
        self.assertIn('if (a != EXPECTED)', changed)
        with self.assertRaises(ValueError):
            t.declarations(text, [('if (a != 4)', 'if (a != EXPECTED)', ['int EXPECTED = 4'])])
        record = 'public record Example(int a) {\n  public Example { if (a != 3) throw new IllegalArgumentException(); }\n}\n'
        changed = t.private_source(record, edits, constants)
        self.assertIn('public record Example(int a) {', changed)
        self.assertIn('public Example { if (a != EXPECTED)', changed)
        self.assertNotIn('public final class Example', changed)


if __name__ == '__main__':
    unittest.main()
