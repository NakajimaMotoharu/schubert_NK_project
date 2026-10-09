import ast
import unittest
from pg836_fixed_handoff import payload
class Test(unittest.TestCase):
    def test_exact_owner_readonly_cohort_and_no_business_operations(self):
        raw=payload();ast.parse(raw)
        for value in ('3412116,16855351','0.1.0-PG796','pg835-pending-codeonly',
                      'knownPreDatabaseOwnerGone=true','signal.SIGTERM','oldCloseUnknown=true',
                      "all(not(task/'children').read_text().strip()",'before==h.snapshot()',
                      '7ea672e8a76c4a4a8a7994652366a4cc','155954641282'):
            self.assertIn(value,raw)
        for value in ('SIGKILL','systemctl start','systemctl stop','3112232','15308543'):
            self.assertNotIn(value,raw)
if __name__=='__main__':unittest.main()
