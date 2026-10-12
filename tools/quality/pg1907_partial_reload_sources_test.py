"""Actual reload-only exports/markers/INVALID originals, independent forbidden actions."""
import ast
import types
import unittest
from unittest.mock import patch
from pyflakes.api import check
from pg1907_partial_reload_sources import sources


class ReloadOnly(unittest.TestCase):
    def test_actual_no_publication_or_exchange_and_complete_consumed_attributes(self):
        s=sources();j=s['Pg1907PartialReload.java'];refs=s['pg1907_native_refs.py']
        self.assertNotIn('candidateReadOnly()',j)
        self.assertIn('phase="ONLY_NORMAL_RELOAD";refs.check("reload");',j)
        self.assertIn('epoch.state()==StartupPermitRecords.State.INVALID',j)
        self.assertIn('pg1895-warning-publication-v1/expected-epoch.private',j)
        self.assertIn('SOURCE="0fd734195b4d5338f6b7e860e087cce561d49562"',j)
        self.assertNotIn('permits.invalidate(',j);self.assertNotIn('Files.move(',j)
        self.assertNotIn('existing_unit.exchange()',refs);self.assertIn('existing_unit.reload()',refs)
        module=types.ModuleType('actual_reload_helper');exec(s['pg1907_native_owned_stop.py'],module.__dict__)
        for n in ast.walk(ast.parse(refs)):
            if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='h':self.assertTrue(hasattr(module,n.attr),n.attr)
        for name,raw in s.items():
            if name.endswith('.py'):self.assertEqual(0,check(raw,'<actual '+name+'>'))

    def test_exact_actual_marker_and_old_original_unit_contract(self):
        s=sources();tree=ast.parse(s['pg1907_input_preflight.py'])
        values=[n.args[0].value for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='print'and n.args and isinstance(n.args[0],ast.Constant)]
        self.assertEqual(['PG1907_INPUT_CLOSURE_READY'],values)
        self.assertIn('"PG1907_INPUT_CLOSURE_READY\\n".getBytes(StandardCharsets.US_ASCII)',s['Pg1907PartialReload.java'])
        helper=types.ModuleType('actual_existing_unit');exec(s['pg1907_existing_unit.py'],helper.__dict__)
        obj=helper.ExistingUnit.__new__(helper.ExistingUnit)
        with patch.object(helper,'rename')as rename:
            with self.assertRaises(ValueError):obj.exchange()
            rename.assert_not_called()
        self.assertIn('metadata9(old)==metadata9(named)',s['pg1907_existing_unit.py'])
        self.assertIn("dir_fd=self.record",s['pg1907_existing_unit.py'])


if __name__=='__main__':unittest.main()
