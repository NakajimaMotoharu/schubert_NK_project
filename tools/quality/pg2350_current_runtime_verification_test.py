import ast
import unittest
from pg2350_current_runtime_verification_sources import sources,CLASS,BEFORE


class VerificationOnly(unittest.TestCase):
    def test_normal_scope_and_zero_business_mutation(self):
        values=sources();self.assertEqual(20,len(values))
        io=values['pg2350_existing_runtime.py'];refs=values['pg2350_native_refs.py']
        for raw in [io,refs]:
            self.assertNotIn('daemon-reload',raw)
            self.assertNotIn('pinned_runtime.reload()',raw)
            self.assertNotIn('os.mkdir(',raw)
        self.assertNotIn('def reload(',io)
        self.assertIn('pinned_runtime.confirm();placed=True',refs)
        self.assertIn('pinned_runtime.close();bus.close()',refs)
        self.assertIn('same_value(now,first)',refs)
        self.assertIn(BEFORE,refs)
        self.assertIn('VERIFICATION_ONLY_CURRENT_RUNTIME',values[CLASS+'.java'])
        self.assertIn('freshResumeRuntimePrepared=false\\nnormalSingleRuntimeReload=false\\nverificationOnlyNormalScope=true\\n',values[CLASS+'.java'])
        self.assertNotIn('freshResumeRuntimePrepared=true',values[CLASS+'.java'])
        self.assertNotIn('normalSingleRuntimeReload=true',values[CLASS+'.java'])
        forbidden={'mkdir','unlink','rename','replace','write','fchmod','chmod','utime'}
        self.assertFalse(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in forbidden for n in ast.walk(ast.parse(io))))


if __name__=='__main__':unittest.main()
