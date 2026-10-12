"""Execute actual host lookup and independently check complete current authority."""
import ast
import unittest
from pg1583_current_stop_independent_post import source,payload

class CurrentPostTest(unittest.TestCase):
    def test_actual_host_complete_hash_lookup_and_absence_refusal(self):
        function=ast.parse(source()).body[0]
        nodes=[n for n in function.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in {'names','hashes'}for t in n.targets)]
        expected=['Pg1579NativeStop.class','Pg1579NativeStop$References.class','pg1579_native_refs.py','pg1579_native_owned_stop.py','pg526_term_witness.py','pg526_native_term_witness.py','pg1579_parent_receipt.py','pg1579_durable.py','pg1579_configuration.py','pg1579_configuration_capture.py','pg1579_row_bound.py','pg1579_stable_journal.py']
        code=compile(ast.Module(body=nodes,type_ignores=[]),'<actual current post complete hash lookup>','exec')
        env={'build':{'fileHashes':{n:'a'*64 for n in expected}}};exec(code,env)
        self.assertEqual(env['names'],expected);self.assertEqual(set(env['hashes']),set(expected))
        for name in expected:
            env={'build':{'fileHashes':{n:'a'*64 for n in expected if n!=name}}}
            with self.assertRaises(KeyError):exec(code,env)

    def test_payload_current_run_seals_and_fixed_generation(self):
        names=['before.private.json','after.private.json','complete.private','parent.private.jsonl']
        seals={n:('abcd'[i]*64)for i,n in enumerate(names)};raw=payload(seals)
        for digest in seals.values():self.assertIn(digest,raw)
        for literal in ['PG1583-current-terminal-post-v1','pg1583-current-terminal-post-v1','pg1579-current-owned-stop-tools-v1','pg1579-native-stop-v1','3d69f5af-6bac-46b1-a540-7591c4a79a0d','0.1.0-PG1544','4d6bcbddb417b76d27e52d5d9640752c300edccf','e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c','9e706936-a3c9-4a09-bb66-e2b1e8bbef66.done','33583425972','108847,158794,159826,161708,118964']:
            self.assertIn(literal,raw)
        self.assertIn("base=W/'pg1583-current-terminal-post-v1'",source())
        self.assertIn("'pg1581-stop-v1.exit'",source())
        for bad in [None,{},dict(seals,foreign='a'*64),dict(seals,**{'before.private.json':'bad'})]:
            with self.assertRaises(ValueError):payload(bad)

if __name__=='__main__':unittest.main()
