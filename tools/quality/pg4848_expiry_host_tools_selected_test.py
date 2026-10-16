import ast
import unittest
from unittest.mock import patch
from pathlib import Path
import pg4848_expiry_host_tools_selected as role


class HostTools(unittest.TestCase):
    def test_current_root_and_all_methods_keep_strict_gates(self):
        raw=role.source();ast.parse(raw)
        self.assertIn(str(role.PG),raw)
        self.assertNotIn("SCHUBERT_PG_ROOT=str(TOOLCHAIN",raw)
        self.assertIn('verifyPriorAudit',raw);self.assertIn('verifyPriorExpiry',raw)
        self.assertIn("'actualMavenExit': code",raw)
        self.assertNotIn('-DfailIfNoTests=false',raw)

    def test_missing_root_refuses_before_maven(self):
        with patch.object(role,'PG',Path('/not-present-pgpt-host-pg')):
            with self.assertRaisesRegex(ValueError,'missing'):role.tools()


if __name__=='__main__':unittest.main()
