import ast
import unittest
from pg4058_original_read_profile_test import GuardTest, guards
import pg4084_recovery_inspection as inspection


class InspectionTest(unittest.TestCase):
    def test_typed_read_only_java_no_expired_parent_authority(self):
        raw = inspection.java()
        for proof in ['MaintenanceFileLock.create().tryExclusive', 'StartupAdmissionFile.create().tryExclusive',
                      'db.setReadOnly(true); db.setAutoCommit(false)', 'permits.readIssued()',
                      'launches.readOwner()', 'launches.readLaunch(ServiceConfigFiles.Service.API)',
                      'launches.readLaunch(ServiceConfigFiles.Service.WEB)', 'epoch.activation().equals(ORIGINAL)',
                      'owner.morning().pid() == 696557', 'owner.morning().startTicks() == 12873540',
                      'api.child().startTicks() == 13004447', 'web.child().startTicks() == 13005817']:
            self.assertTrue(proof in raw, 'actual fixed typed binding required: ' + proof)
        for forbidden in ['.parentsGuard(', '.revoke(', '.retire(', '.start(', 'ProcessBuilder', 'Runtime.exec']:
            self.assertFalse(forbidden in raw, 'inspection cannot acquire expired authority or mutate')

    def test_real_operator_and_pool_guard_closure(self):
        raw = inspection.payload('run'); tree = ast.parse(raw)
        functions = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
        self.assertTrue({'snapshot', 'detailed', 'nss', 'peers', 'tcp_pair', 'same_values'} <= functions)
        self.assertTrue("['units','actors','detailedActors','durable','native','startup','runtime']" in raw)
        self.assertTrue('classid::bigint as classid,objid::bigint as objid' in raw)
        self.assertTrue("compiled['classHashes']" in raw)
        value, _, sockets = GuardTest().fixture(True)
        table = ['header']
        for i, row in enumerate(value['database']['peers']):
            port = row['port']; a, b = str(100 + 2 * i), str(101 + 2 * i)
            table += [f'0: 0100007F:{port:04X} 0100007F:1538 01 0 0 0 0 0 {a}',
                      f'0: 0100007F:1538 0100007F:{port:04X} 01 0 0 0 0 0 {b}']
        ns = guards({'/proc/net/tcp': '\n'.join(table), '/proc/net/tcp6': 'header'}, sockets, raw)
        ns['peers'](value, (140, 240)); value['database']['locks'][0]['objid'] = '71419602'
        with self.assertRaises(ValueError): ns['peers'](value, (140, 240))
        with self.assertRaises(ValueError): inspection.payload('recover')


if __name__ == '__main__': unittest.main()
