"""BUG1250/YKT1016: final transport/server roles, no LAN/VM/test dispatch."""
import inspect
import unittest
from pyflakes.api import check
import pg2750_db_backup_handoff_selected as handoff
import pg2754_retained_backup_selected as retained
import pg2758_backup_completion_selected as completion
import pg2762_post_begin_identity_selected as identity
import pg2736_backup_retention_selected as historical


class CompletedNamespaceTest(unittest.TestCase):
    def test_completed_current_roles_and_fixed_authority(self):
        for module,label,version,launcher in [
            (retained,'PG2754','v3','Pg2754RetainedBackupLauncher'),
            (completion,'PG2758','v1','Pg2758BackupCompletionFailureLauncher'),
            (identity,'PG2762','v1','Pg2762PostBeginIdentityLauncher')]:
            with self.subTest(label=label):
                body=module.transport_body();server=module.server();slot=label+'-selected-'+version
                self.assertEqual(5,body.count(slot))
                for role in ('/runs/'+slot,'/transfer/'+slot+'/','/transfer/'+slot+'/selected.private.py'):
                    self.assertIn(role,body)
                self.assertIn(slot,server);self.assertIn(launcher,server)
                self.assertIn('source-full-PG2744',server);self.assertIn('PG2746-native-v2',server)
                self.assertIn('pg2745-backup-admission-full-qualified-v1',body)
                self.assertEqual(handoff.SOURCE,module.SOURCE)
                self.assertEqual(0,check('INPUT={}\n'+server,'<completed selected namespace>'))
                self.assertNotIn('PG2754-selected-v1',body+server)
                self.assertNotIn('PG2754-selected-v2',body+server)

    def test_before_fix_double_expansion_witness_and_unchanged_actual_ancestors(self):
        intermediate=inspect.getsource(handoff.main).replace('PG2750','PG2754').replace('pg2750','pg2754')
        # The intermediate factory has no completed dispatch literal to replace.
        self.assertNotIn('PG2754-selected-v1',intermediate)
        before=inspect.getsource(handoff.transport.main).replace('PG2220','PG2754')
        self.assertEqual(5,before.count('PG2754-selected-v1'))
        self.assertNotIn('PG2754-selected-v1',retained.transport_body())
        self.assertIn('PG2750-selected-v1',handoff.server())
        self.assertIn('PG2736-selected-v2',historical.server())
        self.assertIn(".replace('PG2736-selected-v1','PG2736-selected-v2')",inspect.getsource(historical.main))


if __name__=='__main__':unittest.main()
