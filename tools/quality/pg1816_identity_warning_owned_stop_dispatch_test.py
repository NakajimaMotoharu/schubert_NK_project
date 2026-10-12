"""Actual source capture/unchanged acceptance and direct real-gate entry."""
from contextlib import contextmanager
import unittest
from unittest.mock import patch
import pg1816_identity_warning_owned_stop_dispatch as actual


class Entry(unittest.TestCase):
    def test_started_source_not_overwritten_by_completion_head(self):
        value=actual.captured_result('71d21e1a3','177967714',143)
        self.assertEqual('71d21e1a3',value['operatorSource']);self.assertEqual('177967714',value['completedObservedHead']);self.assertFalse(value['sourceQualified'])
        self.assertTrue(actual.captured_result('fixed','fixed',0)['sourceQualified'])
        self.assertFalse(actual.captured_result('old','new',0)['sourceQualified'])

    def test_actual_main_gate_for_each_action(self):
        held=[]
        @contextmanager
        def gate(path):
            held.append(path)
            try:yield 11
            finally:held.clear()
        for action in ['stage','stop']:
            def run(selected):self.assertEqual(action,selected);self.assertEqual([actual.P/'current-management-critical.lock'],held);return 0
            with patch.object(actual.sys,'argv',['actual',action]),patch.object(actual,'management_gate',gate),patch.object(actual,'run_action',run):self.assertEqual(0,actual.main())

    def test_stage_namespace_and_old_run_uuid(self):
        self.assertTrue(actual.REMOTE in actual.STAGE);self.assertTrue(actual.GUEST in actual.STAGE)
        self.assertFalse('pg1802'in actual.STAGE);self.assertFalse('pg1800'in actual.STAGE)
        self.assertTrue('4148e3e8-f107-431a-ab27-d6e6d1f1772e'in actual.sources()['pg1808_parent_receipt.py'])


if __name__=='__main__':unittest.main()
