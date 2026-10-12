"""Actual entry/gate exclusion and complete immutable stage namespace."""
import ast
from contextlib import contextmanager
import unittest
from unittest.mock import patch
import pg1802_warning_owned_stop_dispatch as actual


class Direct(unittest.TestCase):
    def test_main_holds_gate_for_both_actual_actions(self):
        held=[]
        @contextmanager
        def gate(path):
            held.append(path)
            try:yield 111
            finally:held.clear()
        for action in ['stage','stop']:
            def run(selected):self.assertEqual(action,selected);self.assertEqual([actual.P/'current-management-critical.lock'],held);return 0
            with patch.object(actual.sys,'argv',['actual',action]),patch.object(actual,'management_gate',gate),patch.object(actual,'run_action',run):self.assertEqual(0,actual.main())
            self.assertEqual([],held)

    def test_busy_gate_cannot_enter_guest_or_action(self):
        run=[]
        with patch.object(actual.sys,'argv',['actual','stop']),patch.object(actual,'management_gate',side_effect=BlockingIOError),patch.object(actual,'run_action',side_effect=lambda a:run.append(a)):
            with self.assertRaises(BlockingIOError):actual.main()
        self.assertEqual([],run)

    def test_exact_current_stage_names(self):
        compile(actual.STAGE,'<actual immutable stage>','exec')
        self.assertFalse('1772'in actual.STAGE);self.assertFalse('1774'in actual.STAGE)
        self.assertTrue(actual.GUEST in actual.STAGE);self.assertTrue(actual.REMOTE in actual.STAGE)
        ast.parse(actual.STAGE)


if __name__=='__main__':unittest.main()
