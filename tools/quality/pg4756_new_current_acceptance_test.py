"""Independent acceptance capsule identity, raw durability ordering and no stale before schema."""
import ast
import unittest
from pyflakes.api import checkPath
from pg4752_new_current_admission_test import NewAdmission
import pg4752_new_current_admission_image as admission
import pg4756_new_current_same_day_rows as rows
import pg4760_new_current_whole_seal as seal


class Acceptance(unittest.TestCase):
    def test_all24_raw_before_parse_and_actual_source_binding(self):
        raw=rows.payload(NewAdmission().binding(),'a'*64)
        self.assertIn("before=json.loads(br)['rows']",raw)
        self.assertLess(raw.index("preserve('sql-stdout.private.jsonl'"),raw.index('for line in r.stdout.splitlines():'))
        self.assertLess(raw.index("preserve('after.private.json'"),raw.index('result=qualify(before,now,'))
        self.assertIn('NKQRY1',raw);self.assertIn(admission.SOURCE,raw)
        self.assertNotIn("json.loads(br)['database']",raw)
        self.assertEqual(0,checkPath(rows.__file__))

    def test_whole_genuine_guard_same_day_capsule_full11_and_source(self):
        raw=seal.payload(NewAdmission().binding(),'a'*64)
        values={t.id:ast.literal_eval(n.value)for n in ast.parse(raw).body if isinstance(n,ast.Assign)for t in n.targets if isinstance(t,ast.Name)and t.id in {'ORACLE','GUARD'}}
        self.assertEqual({'ORACLE','GUARD'},set(values));self.assertIn('NKQRY1',values['ORACLE'])
        self.assertIn("require({'CLEAN_SESSION','CLEAN_LOG','CLEAN_NOTIFICATION'}<=skips)",values['ORACLE'])
        self.assertIn('all64 old native',raw);self.assertNotIn(admission.previous.SOURCE,raw)
        self.assertIn('genuineRootDone',values['GUARD']);self.assertIn('1800',values['GUARD'])
        self.assertIn(seal.SLOT,raw);self.assertNotIn('pg4642-current-whole-seal-v1',raw)
        self.assertEqual(0,checkPath(seal.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
