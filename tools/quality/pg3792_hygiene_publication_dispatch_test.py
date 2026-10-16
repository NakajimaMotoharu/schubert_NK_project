import ast
import unittest
import pg3792_hygiene_publication_dispatch as tool


class Dispatch(unittest.TestCase):
    def test_stage_and_full_body_roles(self):
        ast.parse(tool.STAGE);raw=tool.source();ast.parse(raw)
        for marker in [tool.REMOTE,tool.GUEST,'0.1.0-PG3420',tool.role.BOOT]:self.assertTrue(marker in tool.STAGE,marker)
        self.assertNotIn('/home/ubuntu//',tool.STAGE)
        for marker in ['pg3792-stage-v1.exit','Pg3788TransitionTest',"role.CLASS+' activate'",'finiteCodeOnlyPublication','currentApprovalEpochChanged']:self.assertTrue(marker in raw,marker)
        for marker in ['pg3784','Pg3780','prepare-ro','candidateHostReadonlyOnly']:self.assertFalse(marker in raw,marker)
        self.assertEqual(1,raw.count('with management_gate('))


if __name__=='__main__':unittest.main()
