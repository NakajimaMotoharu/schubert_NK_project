import inspect
import unittest
import xml.etree.ElementTree as ET
from pyflakes.api import check

import pg3348_related_boundary_group as target


class RelatedBoundaryTest(unittest.TestCase):
    def test_expected_all_six_modules_seven_suites_forty_four_cases(self):
        self.assertEqual(6, len(target.CLASSES))
        self.assertEqual(7, sum(len(v) for v in target.CLASSES.values()))
        self.assertEqual(44, sum(n for v in target.CLASSES.values() for n in v.values()))
        self.assertEqual(4, len(target.CHANGED))

    def test_actual_case_sets_and_failure_retry_refusal(self):
        node = ET.Element('testsuite', name='class', tests='2', failures='0', errors='0', skipped='0')
        for name in ['a', 'b']: ET.SubElement(node, 'testcase', classname='class', name=name)
        self.assertEqual({('class', 'a'), ('class', 'b')}, target.classify([node], {'class': 2}))
        node.set('skipped', '1')
        with self.assertRaises(ValueError): target.classify([node], {'class': 2})
        node.set('skipped', '0'); ET.SubElement(node[0], 'flakyFailure')
        with self.assertRaises(ValueError): target.classify([node], {'class': 2})

    def test_complete_payload_no_skip_options_child_mask_and_exit_receipt(self):
        raw = 'INPUT={}\n' + inspect.getsource(target.require) + '\n' + inspect.getsource(target.classify) + '\n' + target.SERVER
        self.assertEqual(0, check(raw, '<related44 namespace>'))
        for forbidden in ['skipTests', 'failIfNoSpecifiedTests', 'systemctl']:
            self.assertNotIn(forbidden, raw)
        self.assertIn('umask=0o027', raw)
        self.assertLess(raw.index("maven-exit.safe.json"), raw.index('genuine selected Maven0'))


if __name__ == '__main__':
    unittest.main()
