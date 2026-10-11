import ast
import unittest
from pg1339_published_stop_independent_post_v3 import source

class ActualPostHostNamesTest(unittest.TestCase):
    def test_actual_composed_names_and_frozen_hash_lookup(self):
        main=ast.parse(source()).body[0]
        assignments=[n for n in main.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in ['names','hashes']for t in n.targets)]
        expected=['Pg1334NativeStop.class','Pg1334NativeStop$References.class','pg1334_native_refs.py','pg1334_native_owned_stop.py','pg526_term_witness.py','pg526_native_term_witness.py','pg1334_parent_receipt.py','pg1334_durable.py','pg1334_configuration.py','pg1334_configuration_capture.py','pg1334_row_bound.py','pg1334_stable_journal.py']
        env={'build':{'fileHashes':{n:'a'*64 for n in expected}}}
        exec(compile(ast.Module(body=assignments,type_ignores=[]),'<actual host names/hash extract>','exec'),env)
        self.assertEqual(env['names'],expected)
        self.assertEqual(set(env['hashes']),set(expected))
        env={'build':{'fileHashes':{n:'a'*64 for n in expected[1:]}}}
        with self.assertRaises(KeyError):exec(compile(ast.Module(body=assignments,type_ignores=[]),'<missing frozen helper refusal>','exec'),env)
        self.assertTrue("replace('1216','1253')"not in source())

if __name__=='__main__':unittest.main()
