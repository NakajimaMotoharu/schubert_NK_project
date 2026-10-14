"""Pure candidate namespace/negative fixtures; no guest/permit/coverage authority."""
import ast
import inspect
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pyflakes.api import check
from pg1446_current_cold_stage import W
from pg2698_operation_admission_before import BODY
import pg2700_operation_current_terminal as t
import pg2702_operation_current_rows as r
import pg2704_operation_current_full_seal as s
import pg2706_operation_current_parent_projection as p


class WholeAcceptancePreparation(unittest.TestCase):
    def test_complete_current_original_readonly_namespace(self):
        self.assertEqual(0,check(BODY,'<actual immutable hash reader>'))
        for m in ['pg2684-operation-current-noargs-once-v2','execEntries','28','41','O_NOFOLLOW','rawExported']:
            self.assertIn(m,BODY)

    def test_read_atime_is_not_content_or_ownership_change(self):
        tree=ast.parse(BODY);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='identity')
        ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'<independent file identity>','exec'),ns)
        expected=dict(st_dev=1,st_ino=2,st_uid=0,st_gid=0,st_mode=0o100600,st_nlink=1,st_size=100,st_mtime_ns=11,st_ctime_ns=12,st_atime_ns=13)
        identity=ns['identity'];base=identity(SimpleNamespace(**expected))
        self.assertEqual(base,identity(SimpleNamespace(**{**expected,'st_atime_ns':100})))
        for key in ['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns']:
            with self.subTest(key=key):self.assertNotEqual(base,identity(SimpleNamespace(**{**expected,key:expected[key]+1})))

    def test_terminal_seal_and_parent_are_new_source_only(self):
        actual=json.loads((W/'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
        historical={**actual['binding'],'rootPid':actual['rootPid']}
        with self.assertRaises(ValueError):t.payload(historical,'a'*64)
        # Clearly typed fixture identifiers are source-construction data only.
        fixture={**historical,'run':'00000000-0000-0000-0000-000000000001','activation':'00000000-0000-0000-0000-000000000002'}
        with patch.object(s,'before',return_value='b'*64):raw=s.payload(fixture,'a'*64)
        ast.parse(raw);self.assertEqual(0,check(raw,'<whole fixture new seal>'))
        for m in [s.SOURCE,s.SLOT,'pg2684-operation-current-noargs-once-v2','pg2654-manifest.sig','b'*64,fixture['run']]:self.assertIn(m,raw)
        parent=p.payload('b'*64,'a'*64);ast.parse(parent)
        for m in [p.SOURCE,'pg2704-operation-current-full-seal-v1','len(fields)==18']:self.assertIn(m,parent)

    def test_transport_and_rows_dependencies_no_old_receipt(self):
        raw=inspect.getsource(r.payload)
        for m in ['pg2686-operation-current-live-binding-v1','pg2684-operation-current-noargs-once-v2','before()']:
            self.assertIn(m,raw)
        for fn in [t.entry,r.entry,s.entry,p.main]:
            ast.parse(inspect.getsource(fn))


if __name__=='__main__':unittest.main()
