"""Final returned stage/host/archive/action bind to one new slot and actual frozen current graph."""
import ast
import unittest
import pg2946_current_resume_dispatch as p


class CurrentDispatch(unittest.TestCase):
    def test_complete_final_stage_and_direct_action(self):
        raw=p.source();stage=p.STAGE
        for value in ['pg2946','pg2944-frozen',p.CLASS,p.TOOLS]:self.assertTrue(value in raw,value)
        for value in ['pg2946','79a3260a-e16d-42bf-942a-b914ed144c28',p.TOOLS]:self.assertTrue(value in stage,value)
        for text in [raw,stage]:
            ast.parse(text)
            for old in ['pg2306','PG2126','b2d6f605','3b7f3567']:self.assertFalse(old in text,old)


if __name__=='__main__':unittest.main()
