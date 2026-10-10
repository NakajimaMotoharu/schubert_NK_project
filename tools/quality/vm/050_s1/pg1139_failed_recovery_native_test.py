import ast
import unittest
from pg1139_failed_recovery_native import source


class NativeTest(unittest.TestCase):
    def test_stage_and_recover_fixed_frozen_byte_closure_no_second_operator(self):
        text = source(); ast.parse(text)
        for value in ['pg1138-failed-recovery-frozen-v3.safe.json', 'pg1134-issued-api-tools-v3',
                      'pg1139-fixed-stage-v1', '0.1.0-PG1068', 'Pg1134SingleApiRecovery',
                      'len(frozen[\'phases\'])==4', 'd5b00104280028d9ea81b44c1d1c805f3c2861ed',
                      "commands=[(SSH+[prefix+'Pg1134SingleApiRecovery '+action],None)]"]:
            self.assertIn(value, text)
        for value in ['Pg1023', '0.1.0-PG932', "prefix+'Pg1134SingleApiIntentTest'"]:
            self.assertNotIn(value, text)
        self.assertNotIn('payload-sha256.json', text)
        self.assertIn("seen==set(FILES)|directories|{'.'}", text)
        self.assertIn("p.relative_to(root).as_posix()for p in root.rglob('*')", text)
        self.assertIn("'finiteRecoveryPlanned':action=='recover'", text)


if __name__ == '__main__': unittest.main()
