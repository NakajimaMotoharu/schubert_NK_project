import ast
import unittest
from pg1478_partial_original_profile_sources import java,refs


class PartialReadonlySourceTest(unittest.TestCase):
    def test_profile_never_prepares_stops_or_repairs_business_state(self):
        source=java()
        for text in ['Pg1478PartialOriginalProfile','"profile".equals(args[0])',
                     '15700a87-9117-4f63-a0ff-768dd604d0f1','proof.completed().isEmpty()',
                     'MaintenanceFileLock.create().tryExclusive','StartupAdmissionFile.create().tryExclusive',
                     'database.setReadOnly(true)','lease.confirmClosed()','refs.release()',
                     'twoWholeGraphObservationsNanos']:
            self.assertIn(text,source)
        for text in ['freezeCandidate','initialChild','environment();','done.outcome()',
                     'systemctl','invalidate(','.issue(','.retire(','.complete(']:self.assertNotIn(text,source)

    def test_current_capture_all_fields_not_cold_or_partial_expected(self):
        source=refs();tree=ast.parse(source)
        funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
        snap=ast.unparse(funcs['snapshot'])
        self.assertIn('expected_current',source);self.assertIn('value == expected_current',ast.unparse(tree))
        self.assertNotIn('statusSha256',snap)
        self.assertNotIn('peers.splitlines()',snap)
        for text in ['tenFull','StartupLaunchFiles']:self.assertNotIn(text,snap)
        self.assertIn("m['ExecMainStatus'] == '143'",snap)
        self.assertIn('peer_check()',source)
        self.assertIn("b'Pg1478PartialOriginalProfile'",ast.unparse(funcs['actor']))
        self.assertIn("b'profile'",ast.unparse(funcs['actor']))
        self.assertIn('PG266-readonly-profile',ast.unparse(funcs['peer_check']))
        calls=[ast.unparse(n.func)for n in ast.walk(tree)if isinstance(n,ast.Call)]
        for text in ['manager.StartUnit','manager.StopUnit','os.kill','signal.pidfd_send_signal']:self.assertNotIn(text,calls)

    def test_paired_namespace_bindings_before_full_snapshot(self):
        source=refs();tree=ast.parse(source)
        snapshot_index=next(i for i,n in enumerate(tree.body)if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
        prefix=tree.body[:snapshot_index];before=ast.unparse(ast.Module(body=prefix,type_ignores=[]))
        for symbol in ['CONFIG_FIELDS','CONFIG_CONTRACT','UNIT_VECTOR','CAPTURE_BOUND','contract','locks']:
            self.assertIn(symbol,before)
        # Actual config/parser namespaces must have their accompanying exec,
        # not merely a same-named assignment (previous BUG1102).
        self.assertGreaterEqual(sum(isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and ast.unparse(n.value.func)=='exec'for n in prefix),3)


if __name__=='__main__':unittest.main()
