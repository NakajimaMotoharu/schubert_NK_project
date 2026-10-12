"""Execute complete host ABI lookup; independently require current finite delta."""
import ast
import unittest
from pg1595_current_runtime_retired_post import payload,source

class CurrentRetiredPostTest(unittest.TestCase):
    def test_actual_fixed_current_seals_delta_and_file_lookup(self):
        seals={n:'a'*64 for n in ['before.private.json','after.private.json','complete.private','parent.private.jsonl']}
        raw=payload(seals);self.assertIn('retirement.same_except_runtime(before,after',raw)
        for v in ['pg1591-native-stop-v1','pg1591-current-runtime-retirement-tools-v1','6fe760da139eae3115363192c24fdff981bcdc6f7849016c18c7fe60b6c1fca7','2c20987e1457942dc196a1f591b4cd925bac1da2d689421a6782ba4d3eb31f35','runtimeRetiredOnly=true','allTenAlreadyTerminal=true','PG1595-current-runtime-retired-post-v1']:
            self.assertIn(v,raw)
        self.assertIn("'ownedExplicitStops':0",raw)
        self.assertNotIn("'ownedExplicitStops':4",raw)
        main=ast.parse(source()).body[0]
        assignments=[n for n in main.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in {'names','hashes'}for t in n.targets)]
        expected=['Pg1591NativeStop.class','Pg1591NativeStop$References.class','pg1591_native_refs.py','pg1591_native_owned_stop.py','pg526_term_witness.py','pg526_native_term_witness.py','pg1591_parent_receipt.py','pg1591_durable.py','pg1591_configuration.py','pg1591_configuration_capture.py','pg1591_row_bound.py','pg1591_stable_journal.py']
        env={'build':{'fileHashes':{n:'a'*64 for n in expected}}};exec(compile(ast.Module(body=assignments,type_ignores=[]),'<actual new retirement helper names>','exec'),env)
        self.assertEqual(env['names'],expected);self.assertEqual(set(env['hashes']),set(expected))

if __name__=='__main__':unittest.main()
