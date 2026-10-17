"""Independent fixed current-generation input closure, real entry guards, no VM actions."""
import inspect
import unittest
from pathlib import Path
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4932_current_bootstrap_sources as role
import pg4934_current_bootstrap_compile as compiler
import pg4936_current_bootstrap_dispatch as dispatch


class CurrentBootstrap(unittest.TestCase):
    def test_actual_full_current_graph_and_no_old_authority(self):
        values=role.files(role.BASELINE)
        java=values['Pg4932BootstrapExisting.java'];helper=values['pg4932_bootstrap_existing.py']
        for value in ('expectedBeforeOwnership(2,"schubert_batch","PG4932-bootstrap-guard"',role.SOURCE):self.assertIn(value,java)
        for value in ('==884',role.BASELINE,role.before.SLOT,'199849150395','7fe303d625de4a83b23d23fca4eca2bb','7bae6042-b79f-4fb2-9d9f-edf47b428cbe'):
            self.assertIn(value,helper)
        self.assertIn('4e220f3b-fbb4-411c-b5c4-7ca1371daa20',values['pg4916_parent_receipt.py'])
        self.assertIn(role.BOM,values['pg4932_input_preflight.py'])
        self.assertEqual(values['pg4916_parent_receipt.py'],(role.W/role.owned.TOOLS/'pg4916_parent_receipt.py').read_text())
        for name,raw in values.items():
            if name.endswith('.py'):self.assertEqual(0,check(raw,'<actual current Bootstrap '+name+'>'))
            for old in ('Pg4820','PG4702','pg4702','pg4818-new-current','pg4772_parent_receipt','fff841d9-2554','189659374308'):
                self.assertNotIn(old,raw,name)

    def test_missing_foreign_current_eligibility_rejected_before_emit(self):
        with self.assertRaisesRegex(ValueError,'actual4930'):role.files('0'*64)
        with patch.object(role,'eligibility',side_effect=ValueError('not current')):
            with self.assertRaisesRegex(ValueError,'not current'):role.files(role.BASELINE)
        original=(role.W/role.before.SLOT/'manifest.safe.json').read_bytes()
        import json
        for field,bad in [('actualExit',1),('source',role.previous.SOURCE)]:
            value=json.loads(original);value[field]=bad
            with patch.object(Path,'read_bytes',return_value=json.dumps(value).encode()),self.assertRaises(ValueError):role.eligibility(role.BASELINE)

    def test_current_complete_compile_and_closed_stage_contract(self):
        raw=compiler.source();self.assertIn('pg4918-frozen-v1.safe.json',raw);self.assertIn('pg4860-release-v1',raw)
        self.assertIn('pg4934-frozen-v1.safe.json',raw);self.assertIn('target.rglob',raw)
        self.assertNotIn('pg4774-',raw);self.assertNotIn('pg4702-',raw)
        header=inspect.getsource(compiler.previous.previous).split('\ndef main():',1)[0]
        header=header.replace('import pg4820_new_current_bootstrap_sources as role','import pg4932_current_bootstrap_sources as role')
        self.assertEqual(0,check(header+'\n'+raw,'<actual nested ABI complete namespace>'))
        ns=dispatch.namespace();self.assertIn('inventory',ns['STAGE']);self.assertIn('PG4860',ns['STAGE'])
        self.assertNotIn('PG4702',ns['STAGE'])
        scope={};exec(compile(ns['STAGE'].split('os.umask(0o077)')[0],'<pure archive guard definitions>','exec'),scope)
        with self.assertRaises(ValueError):scope['inventory']({'../escape':'a'*64})
        strings={n for n in ns['main'].__code__.co_consts if isinstance(n,str)}
        for value in ('execute','-verify-v1.safe.json','-stage-v1.safe.json','.requested','once phase already reserved, recover original only','Pg4932'):self.assertIn(value,strings)
        for value in ('PG4702','Pg4820'):
            self.assertFalse(any(value in s for s in strings),value)
        for path in (role.__file__,compiler.__file__,dispatch.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
