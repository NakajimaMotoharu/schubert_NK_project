import ast
import inspect
import unittest
from unittest.mock import patch
import pg3784_hygiene_ro_dispatch as tool


class Dispatch(unittest.TestCase):
    def test_stage_roles_and_single_gate(self):
        ast.parse(tool.STAGE)
        for marker in [tool.REMOTE,tool.GUEST,'0.1.0-PG3420',tool.role.unused.BOOT]:self.assertIn(marker,tool.STAGE)
        for marker in ['pg3442','pg3446','PG2802']:self.assertNotIn(marker,tool.STAGE)
        self.assertIn(repr(tool.REMOTE+'/'+tool.role.TOOLS+'.tar'),tool.STAGE)
        self.assertNotIn('/home/ubuntu//',tool.STAGE)
        self.assertIsInstance(tool.template.old.previous.previous.prior.prior.prior.OPTIONS,list)
        raw=inspect.getsource(tool.main)
        self.assertEqual(1,raw.count('with management_gate('))
        self.assertIn('one reserved action only',raw)
        self.assertNotIn('start-unit',raw)
        with patch.object(tool.sys,'argv',['tool','publish']):
            with self.assertRaises(ValueError):tool.main()


if __name__=='__main__':unittest.main()
