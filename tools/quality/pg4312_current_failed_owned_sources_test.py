"""Independent current literal/epoch vector and immutable shared terminal mechanics."""
import ast
import unittest
from pyflakes.api import check
import pg4312_current_failed_owned_sources as s
import pg4312_current_failed_owned_stage as stage


class CurrentSource(unittest.TestCase):
    def test_positive_current_literals_and_no_old_java_byte_reuse(self):
        java=s.java()
        for text in ['b1ba37cb-9b2b-469b-a5f2-b0e6d8c97cd1','2026-10-16T11:32:53.943173Z','8314450e-0dd5-4986-875c-81f73e1b50b2','bbcdb69957764d489a9c757b441542fd','795724','14962226','807944','15096765','808319','15098199']:self.assertIn(text,java)
        for old in ['dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f','820851b8291a4c958bb34f6c48430ca3','758821','759868','696557']:self.assertNotIn(old,java)
        raw=stage.payload();self.assertEqual(check(raw,'<full new current compile>'),0)
        self.assertIn('/opt/jdk-25.0.4/bin/javac',raw);self.assertNotIn('No javac:',raw)

    def test_new_epoch_independent_literal_and_foreign_negative(self):
        ns={};exec(s.files()['recovery_plan.py'],ns)
        original=b'NKEPOCH1\nstate=ISSUED\nboot_id=79a3260a-e16d-42bf-942a-b914ed144c28\nepoch_id=33333333-3333-4333-8333-333333333333\nrun_id=b1ba37cb-9b2b-469b-a5f2-b0e6d8c97cd1\ncutoff_utc=2026-10-16T11:32:53.943173Z\nactivation_id=8314450e-0dd5-4986-875c-81f73e1b50b2\npermit_sha256='+b'a'*64+b'\n'
        expected=b'NKEPOCH1\nstate=INVALID\nboot_id=79a3260a-e16d-42bf-942a-b914ed144c28\nepoch_id=33333333-3333-4333-8333-333333333333\nrun_id=b1ba37cb-9b2b-469b-a5f2-b0e6d8c97cd1\ncutoff_utc=2026-10-16T11:32:53.943173Z\nactivation_id=8314450e-0dd5-4986-875c-81f73e1b50b2\npermit_sha256=-\n'
        self.assertEqual(ns['invalid_epoch'](original),expected)
        for bad in [None,b'',original.replace(b'NKEPOCH1',b'UNKNOWN'),original.replace(b'b1ba37cb-9b2b-469b-a5f2-b0e6d8c97cd1',b'dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f'),original.replace(b'\n',b'\r\n'),expected]:
            with self.assertRaises(ValueError):ns['invalid_epoch'](bad)

    def test_shared_terminal_sources_and_six_stop_order_unchanged(self):
        original=s.previous.files();current=s.files()
        for name,value in original.items():
            if name not in {'RootFailedDoneRecovery.java','recovery_plan.py'}:self.assertEqual(current[name],value)
        before=ast.parse(original['recovery_plan.py']);after=ast.parse(current['recovery_plan.py'])
        get=lambda tree:ast.dump(next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='Plan'))
        self.assertEqual(get(before),get(after))


if __name__=='__main__':unittest.main()
