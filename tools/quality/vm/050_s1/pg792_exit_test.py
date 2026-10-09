"""Literal normal/nonzero exit and exactly-one independent postcheck."""
import unittest
from pg792_selected_qualify import invoke_then_check


class Test(unittest.TestCase):
    def test_all_exit_paths(self):
        for code in (None,0):
            events=[]
            def action():events.append('run');raise SystemExit(code)
            self.assertEqual('qualified',invoke_then_check(action,lambda:events.append('check')or'qualified'));self.assertEqual(['run','check'],events)
        self.assertEqual(17,invoke_then_check(lambda:None,lambda:17))
        for code in (1,143,'failed'):
            events=[]
            def action():raise SystemExit(code)
            with self.assertRaises(SystemExit)as result:invoke_then_check(action,lambda:events.append('invalid'))
            self.assertEqual(code,result.exception.code);self.assertEqual([],events)


if __name__=='__main__':unittest.main()
