"""Actual complete managed capture/DB/phase/native oracle and immutable Root tuples."""
import ast
import unittest
import pg1372_bootstrap_role_sources as p

class Test(unittest.TestCase):
    def test_actual_full_payload_and_canonical_phase_matrix(self):
        raw=p.helper();tree=ast.parse(raw)
        capture=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='capture')
        self.assertEqual(['present'],[a.arg for a in capture.args.args])
        for value in ("lines[-2:] == ([b'1', b'1'] if present else [b'0', b'0'])",
                      "str(parent)","PG998-bootstrap-role",'policy.before_valid(prior)',
                      'policy.delta(prior,now,lower,upper)',"strict(pathlib.Path(BASE),0o600,67108864)",
                      "a[-3:]==[b'Pg1372BootstrapRolePreparation',b'prepare',b'']"):
            self.assertTrue(value in raw,value)
        self.assertTrue("state='BEFORE'"in raw and "state='PREPARED'"in raw and "state='CLOSED'"in raw)
        self.assertTrue('while True:time.sleep(1)'in raw)
        self.assertTrue(raw.index('for u in UNITS:manager.LoadUnit')<raw.index('initial=capture(True)'))
        self.assertTrue('769ddb15cd735c25fef581b5f9850ef9d0053c0f'in raw)
        self.assertTrue('841b507c-2713-4ffe-8882-68f5fb3f87f5'in raw)
        self.assertFalse('systemctl start'in raw)
        self.assertFalse('pidfd_send_signal'in raw)

    def test_actual_java_single_role_and_resource_close_order(self):
        java=p.files()['Pg1372BootstrapRolePreparation.java']
        for value in ('database.setReadOnly(true)', 'lease.confirmClosed()',
                      'Pg1370BootstrapRoleDirectory.prepare(common,"ordinary-bootstrap196",999,981)',
                      'PG998-bootstrap-role','841b507c-2713-4ffe-8882-68f5fb3f87f5',
                      '2026-10-10T23:54:39.918039Z','signedOriginal();database.rollback()'):
            self.assertTrue(value in java,value)
        self.assertTrue(java.index('lease.confirmClosed()')<java.index('refs.check("closed")'))
        self.assertTrue(java.index('refs.check("closed")')<java.index('refs.release()'))
        self.assertTrue(java.index('ALL_INNER_NORMAL')<java.index('COMPLETE_PUBLISH'))
        self.assertFalse('setReadOnly(false)'in java)
        self.assertFalse('systemctl'in java)

if __name__=='__main__':unittest.main()
