import unittest
import pg5958_private_lock_reason_review as t


class ChangedSourceDiagnosticMappingTest(unittest.TestCase):
    def test_each_independent_fact_gate_must_be_zero(self):
        good = dict(source=t.SOURCE, actualExit=0, compileExit=0, independentFixtureExit=0)
        t.require_facts(good)
        for key in ('actualExit', 'compileExit', 'independentFixtureExit'):
            for value in (1, -1, None, False):
                with self.assertRaises(ValueError):
                    t.require_facts(dict(good, **{key: value}))
            with self.assertRaises(ValueError):
                t.require_facts({k:v for k,v in good.items() if k != key})
        with self.assertRaises(ValueError):
            t.require_facts(dict(good, compileExit=1, independentFixtureExit=1))
        with self.assertRaises(ValueError):
            t.require_facts(dict(good, source='old'))

    def row(self, ident, line, column=3):
        return dict(findingId=ident, sourcePath='Main.java', rule='Rule', priority='2', diagnosticTextSha256='same', identitySchema=2,
                    beginline=str(line), endline=str(line), begincolumn=str(column), endcolumn=str(column+2))

    def test_whole_diagnostic_sequence_and_exact_line_translation(self):
        before = 'header\n  one();\n  two();\n'; after = 'changed header\ninserted\n  one();\n  two();\n'
        old, new = [self.row('a', 2), self.row('b', 3)], [self.row('c', 3), self.row('d', 4)]
        self.assertEqual('b', t.moved_pairs(old, new, set(), before, after)['d'][0]['findingId'])
        for bad in ([new[1], new[0]], new[:1], [dict(new[0], diagnosticTextSha256='other'), new[1]]):
            with self.assertRaises(ValueError):
                t.moved_pairs(old, bad, set(), before, after)


if __name__ == '__main__':
    unittest.main()
