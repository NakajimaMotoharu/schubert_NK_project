"""Pure full post binding tests; neither operations nor actual post are executed."""
import ast
import base64
import unittest
from pyflakes.api import check
import pg4324_current_failed_post as p
from pg4316_current_failed_dispatch_test import assignment


class PostTest(unittest.TestCase):
    def test_current_profile_helpers_failed_contract_and_before_oracle(self):
        raw=p.payload();self.assertEqual(check(raw,'<whole independent current post>'),0)
        self.assertEqual(base64.b64decode(assignment(raw,'JAVA_B64')),p.profile.java().encode())
        self.assertEqual(assignment(raw,'HELPERS'),p.recovery.compiled()['inputFileHashes'])
        self.assertEqual(assignment(raw,'PARENT_SOURCE'),p.recovery.parent_source())
        self.assertIn(p.recovery.SLOT+'-recover',raw);self.assertIn(p.profile.SLOT,raw)
        self.assertIn("before['database']['rows']",raw)
        self.assertIn("declaration_contract['same_configurations']",raw)
        self.assertIn('all37StartupEntriesPreserved',raw)
        for old in ['pg4112-canonical-epoch-owned-tools-v1','pg4146-complete-signed-owned-recovery-v1','pg4072-failed-parent-pid1-read-v1']:
            self.assertNotIn(old,raw)

    def test_no_business_mutating_commands_or_normal_parent_forgery(self):
        raw=p.payload()
        for n in ast.walk(ast.parse(raw)):
            if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in {'run','check_output','Popen'}:
                text=ast.get_source_segment(raw,n)
                for forbidden in ["'systemctl','start'","'systemctl','stop'","'systemctl','daemon-reload'"]:self.assertNotIn(forbidden,text)
        self.assertIn("'oldParentNormal':False",raw)
        self.assertIn("'nativeQualificationPending':True",raw)


if __name__=='__main__':unittest.main()
