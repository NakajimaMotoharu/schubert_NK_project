import ast
import unittest
from pyflakes.api import check
import pg4234_canonical_fresh_noargs_once as p
import pg4138_independent_revoked_epoch as oracle


class CanonicalEntryTest(unittest.TestCase):
    def vector(self):
        return ('NKEPOCH1\nstate=INVALID\nboot_id=79a3260a-e16d-42bf-942a-b914ed144c28\nepoch_id=12345678-1234-4234-9234-123456789abc\nrun_id=dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f\ncutoff_utc=2026-10-16T05:44:47.267413Z\nactivation_id=d9d58371-bf80-49f6-bad9-3d1e0916fb04\npermit_sha256=-\n').encode('ascii')

    def test_ss089_independent_full_golden_vector_and_negative_boundaries(self):
        actual=self.vector();expected=actual.replace(b'state=INVALID',b'state=ISSUED').replace(b'permit_sha256=-',b'permit_sha256='+b'a'*64)
        self.assertEqual(expected,oracle.former_issued(actual,'a'*64))
        for bad in [actual.split(b'\n',1)[1],actual.replace(b'NKEPOCH1',b'OTHER'),actual.replace(b'INVALID',b'ISSUED'),actual.replace(b'\n',b'\r\n'),actual[:-1],actual.replace(b'cutoff_utc',b'cutoff'),actual.replace(b'2026-10-16T05:44:47.267413Z',b'2026-10-16T05:44:48.267413Z'),actual.replace(b'12345678-1234-4234-9234-123456789abc',b'../../foreign'),None]:
            with self.subTest(badHash=hash(bad)),self.assertRaises(ValueError):oracle.former_issued(bad,'a'*64)

    def test_complete_namespace_validation_before_filename_and_one_start(self):
        raw=p.payload({});self.assertEqual(0,check(raw,'<full canonical entry>'));tree=ast.parse(raw)
        self.assertTrue(raw.index("validated=epoch_contract['former_issued']")<raw.index("permit=epoch_path.parent/(epoch_id+'.permit')"))
        self.assertTrue("save=base/'pg4234-canonical-fresh-noargs-once-v1-prestart'"in raw)
        self.assertTrue("save=base/'pg4234-canonical-fresh-noargs-once-v1'"in raw)
        self.assertFalse("epoch.startswith(b'state=INVALID"in raw)
        separators=[n.args[0].value for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='split'and isinstance(n.func.value,ast.Call)and isinstance(n.func.value.func,ast.Attribute)and n.func.value.func.attr=='decode'and n.args and isinstance(n.args[0],ast.Constant)]
        self.assertIn('\n',separators)
        starts=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='run'and n.args and isinstance(n.args[0],ast.List)and any(isinstance(x,ast.Constant)and x.value=='start'for x in n.args[0].elts)]
        self.assertEqual(1,len(starts))


if __name__=='__main__':unittest.main()
