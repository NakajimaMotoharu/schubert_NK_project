import ast
import json
import unittest
import pg3792_hygiene_publication_dispatch as tool


class Dispatch(unittest.TestCase):
    def test_stage_and_full_body_roles(self):
        ast.parse(tool.STAGE);raw=tool.source();ast.parse(raw)
        for marker in [tool.REMOTE,tool.GUEST,'0.1.0-PG3420',tool.role.BOOT]:self.assertTrue(marker in tool.STAGE,marker)
        self.assertNotIn('/home/ubuntu//',tool.STAGE)
        for marker in ['pg3792-stage-v1.exit','Pg3788TransitionTest',"role.CLASS+' activate'",'finiteCodeOnlyPublication','currentApprovalEpochChanged']:self.assertTrue(marker in raw,marker)
        for marker in ['pg3784','Pg3780','pg3782','prepare-ro','candidateHostReadonlyOnly']:self.assertFalse(marker in raw,marker)
        self.assertEqual(1,raw.count('with management_gate('))

    def test_same_source_different_tool_kind_and_missing_entry_rejected(self):
        ro=json.loads((tool.role.W/'pg3782-frozen-v1.safe.json').read_bytes())
        valid=json.loads((tool.role.W/'pg3790-frozen-v1.safe.json').read_bytes())
        tool.qualify_fixed(valid)
        with self.assertRaises(ValueError):tool.qualify_fixed(ro)
        for change in [{'candidateSource':'f'*40},{'actualExit':1},{'fileHashes':{k:v for k,v in valid['fileHashes'].items()if k!='Pg3788TransitionTest.class'}}]:
            with self.assertRaises(ValueError):tool.qualify_fixed({**valid,**change})
        raw=tool.source();self.assertLess(raw.index('qualify_fixed(fixed)'),raw.index("base=W/('pg3792-'"))


if __name__=='__main__':unittest.main()
