import unittest
from unittest.mock import patch
import pg6844_observation_boundaries_selected as p


class ObservationBoundaryDefinitionTest(unittest.TestCase):
    def test_actual_declarations_and_old_wrong_suite_count_rejected(self):
        cases,counts=p.inventory()
        self.assertEqual((23,11),(sum(counts.values()),len(counts)))
        self.assertEqual({'protocol','storage','bootstrap','api','web','batch'},set(cases))
        with patch.object(p,'EXPECTED',(23,10)),self.assertRaises(ValueError):p.inventory()

    def test_only_two_new_tests_and_no_main_or_quality_changes(self):
        new='\n'.join(sorted(p.TESTS))+'\n'
        with patch.object(p.subprocess,'check_output',side_effect=[new,''])as git:
            p.guard('candidate');self.assertEqual(2,git.call_count)
        for paths in ('',new+'src/schubert-nk-api/src/main/java/Unexpected.java\n'):
            with patch.object(p.subprocess,'check_output',return_value=paths)as git:
                with self.assertRaises(ValueError):p.guard('candidate')
                self.assertEqual(1,git.call_count)
        with patch.object(p.subprocess,'check_output',side_effect=[new,'changed gate'])as git:
            with self.assertRaises(ValueError):p.guard('candidate')
            self.assertEqual(2,git.call_count)


if __name__=='__main__':unittest.main()
