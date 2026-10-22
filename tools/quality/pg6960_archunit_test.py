"""Management parser invariants, separate from Java canaries and original PT."""
import unittest

import pg6960_archunit as subject


def report():
    return ('ARCHUNIT\t1.4.2\t6\t6\n'
            + ''.join('MODULE\t'+m+'\t1\n' for m in subject.MODULES)
            + ''.join('RULE\t'+r+'\t0\n' for r in sorted(subject.RULES))
            + 'INSPECTED\t10\t8\n')


class ArchitectureResultTest(unittest.TestCase):
    def test_exact_positive_and_one_declared_violation(self):
        text = report()
        self.assertEqual(6, subject.parse(text)['imported'])
        bad = text.replace('RULE\tMODULE_EDGES\t0', 'RULE\tMODULE_EDGES\t1')
        bad += 'FINDING\tMODULE_EDGES\tweb.Bad\tapi.Bad\n'
        self.assertEqual('MODULE_EDGES', subject.parse(bad)['findings'][0]['rule'])

    def test_vacuous_missing_duplicate_or_unaccounted_result_is_refused(self):
        text = report()
        for bad in (text.replace('6\t6','6\t5',1),
                    text.replace('MODULE\tapi\t1\n',''),
                    text.replace('MODULE\tapi\t1','MODULE\tapi\t0'),
                    text.replace('RULE\tINTERNAL_OWNER\t0\n',''),
                    text+'RULE\tMODULE_EDGES\t0\n',
                    text+'FINDING\tMODULE_EDGES\tweb.Bad\tapi.Bad\n',
                    text.replace('INSPECTED\t10','INSPECTED\t0'),
                    text+'silently ignored output\n'):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                subject.parse(bad)

    def test_failure_counts_must_join_same_rule_not_just_total(self):
        text = report().replace('RULE\tMODULE_EDGES\t0','RULE\tMODULE_EDGES\t1')
        with self.assertRaises(ValueError):
            subject.parse(text+'FINDING\tFRAMEWORK_FENCES\tweb.Bad\tapi.Bad\n')


if __name__ == '__main__':
    unittest.main()
