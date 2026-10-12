"""Actual new keys/exports and fixed producer literals before any new target/ownership."""
import ast
import types
import unittest
from pyflakes.api import check
from pg1913_direct_partial_reload_sources import sources


class Direct(unittest.TestCase):
    def test_actual_keys_and_all_exported_consumer_attributes(self):
        s=sources()
        self.assertIn('pg1913_native_refs.py',s);self.assertIn('Pg1913PartialReload.java',s)
        self.assertNotIn('pg1877_native_refs.py',s);self.assertNotIn('pg1907_native_refs.py',s)
        h=types.ModuleType('actual_direct_h');exec(s['pg1913_native_owned_stop.py'],h.__dict__)
        for n in ast.walk(ast.parse(s['pg1913_native_refs.py'])):
            if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='h':self.assertTrue(hasattr(h,n.attr),n.attr)
        self.assertEqual('/var/lib/pgpt-s1-preservation/pg1917-partial-reload-v1',str(h.ROOT))
        self.assertIn('"PG1913_INPUT_CLOSURE_READY\\n".getBytes(StandardCharsets.US_ASCII)',s['Pg1913PartialReload.java'])
        tree=ast.parse(s['pg1913_input_preflight.py']);prints=[n.args[0].value for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='print'and n.args and isinstance(n.args[0],ast.Constant)]
        self.assertEqual(['PG1913_INPUT_CLOSURE_READY'],prints)
        for name,body in s.items():
            if name.endswith('.py'):self.assertEqual(0,check(body,'<actual direct '+name+'>'))


if __name__=='__main__':unittest.main()
