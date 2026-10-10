"""SSC248 independent pre-Ref fixed actor/RODB/no mutation/once ordering oracles."""
import ast
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from pg1077_cold_candidate_tree_preflight import payload
from pg1078_cold_candidate_tree_handoff import handoff


class Fixed(unittest.TestCase):
    def test_preflight_exact_actor_generation_error_and_prepared_scope(self):
        p=payload();ast.parse(p)
        self.assertIn('2433710',p);self.assertIn('2433776',p)
        self.assertIn("env['OWNER_PID'] = 11678",p)
        self.assertIn("env['PREPARED'] = True",p)
        self.assertNotIn('readonly_runtime_namespaces',p)
        self.assertIn("set(child['fds']) == {'0', '1', '2'}",p)
        self.assertIn('childNoBus',p)
        self.assertNotIn('childBusUniqueName',p)
        self.assertIn('BYTE_AUTH type=ValueError',p)
        self.assertNotIn('pidfd_send_signal',p)
        self.assertNotIn("/proc/5463",p)
        self.assertNotIn("/proc/5489",p)

    def test_once_tree_parent_then_child_scope_no_invented_bus(self):
        h=handoff();ast.parse('if True:\n'+h)
        self.assertNotIn('CHILD_BUS',h)
        self.assertIn("qualified.pop('childNoBus')is True",h)
        self.assertIn('tree_contract.once_tree((11678,2433710),(11704,2433776)',h)
        self.assertIn('contract.durable_reservation',h)
        self.assertLess(h.index('phase=\'FIXED_TREE_BEFORE\''),h.index('phase=\'ONCE_FIXED_TREE_TERM\''))
        self.assertIn("env['OWNER_PID']=0;env['OWNER_BACKEND']=0",h)
        self.assertIn("assert not pathlib.Path('/proc/11704').exists()",h)
        self.assertNotIn('SIGKILL',h)
        self.assertNotIn('terminate_backend',h)

    def test_full_handoff_assembly_independent_receipt_fixture_has_fixed_imports(self):
        import pg1078_cold_candidate_tree_handoff as subject
        with tempfile.TemporaryDirectory(prefix='pg1078-assembly-fixture-')as directory:
            root=Path(directory);out=root/'pg1077-cold-candidate-tree-preflight-v1';out.mkdir()
            (out/'manifest.safe.json').write_text(json.dumps({'actualExit':0,'observed':{'observerNormalClose':True,'beforePrivateSha256':'0'*64}}))
            with patch.object(subject,'W',root):text=subject.payload()
        ast.parse(text)
        self.assertIn('import dbus, time, stat, re, signal, select',text)
        self.assertIn('tree_contract = types.ModuleType',text)
        self.assertIn('tree_contract.once_tree((11678, 2433710), (11704, 2433776)',text)
        self.assertIn('CORE_COUNT = len(held)',text)
        self.assertIn("qualified.pop('childNoBus') is True",text)
        self.assertNotIn('CHILD_BUS',text)


if __name__=='__main__':unittest.main()
