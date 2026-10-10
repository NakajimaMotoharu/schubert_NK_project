import ast
import unittest
from pg1146_terminal_cleanup_native import source


class TransportTest(unittest.TestCase):
    def test_all_frozen_and_stage_slots_new_current_source_bounded(self):
        text=source();ast.parse(text)
        for part in ['pg1145-terminal-frozen-v1.safe.json','pg1144-terminal-tools-v1','Pg1144SingleApiRecovery',
                     'pg1146-fixed-stage-v1','pg1146-stage-v1.exit',"'pg1146-'+action+'-v1'",'directories|{\'.\'}',
                     'finiteRecoveryPlanned', 'd5b00104280028d9ea81b44c1d1c805f3c2861ed']:
            self.assertTrue(part in text,part)
        for part in ['pg1139-fixed-stage-v1','pg1138-failed-recovery-frozen-v3.safe.json','Pg1134SingleApiRecovery']:
            self.assertFalse(part in text,part)


if __name__=='__main__':unittest.main()
