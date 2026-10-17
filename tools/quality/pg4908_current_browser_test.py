import ast
import inspect
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4900_current_admission_image as admission
import pg4906_current_whole_seal as root
import pg4908_current_browser_ready as ready
import pg4910_current_same_owner_browser as actual
import pg4912_current_browser_composite as composite
import pg4914_current_parent_projection as projection


class Browser(unittest.TestCase):
    def test_identity_only_freeze_exact_twelve_cases_and_current_source(self):
        self.assertEqual(admission.SOURCE,ready.SOURCE)
        self.assertIn('tools/quality/pg4908_current_browser_ready.py',ready.PINNED)
        for name in ready.shared.JAVA_INPUTS:
            raw=(ready.shared.ROOT/name).read_text()
            if name not in ready.shared.SHARED:
                self.assertEqual(1,raw.count(ready.shared.OLD));bound=raw.replace(ready.shared.OLD,ready.SOURCE)
                self.assertEqual(raw,bound.replace(ready.SOURCE,ready.shared.OLD))
        self.assertIn("['plannedCases']==12",inspect.getsource(ready.shared.require_ready))

    def test_no_browser_without_genuine_cohort_and_current_owned_socks(self):
        with patch.object(actual,'receipt',side_effect=ValueError('genuine current missing')),self.assertRaisesRegex(ValueError,'genuine current missing'):actual.guard()
        body=inspect.getsource(actual.previous.previous.main)
        self.assertLess(body.index('ready.require_ready()'),body.index('subprocess.run(command,'))
        self.assertIn('before_socks==previous.previous.owned_socks()',body)

    def test_actual_guard_changes_only_one_current_release_authority(self):
        original=(admission.W/'pg4910-current-same-owner-browser-v1/guard.private.py').read_text()
        expected=original.replace('/opt/schubert-nk/releases/0.1.0-PG3976','/opt/schubert-nk/releases/0.1.0-PG4860',1)
        current=actual.guard()
        self.assertEqual(expected,current)
        self.assertEqual(0,check(current,'<actual complete Browser guard>'))
        self.assertIn(admission.SOURCE,current);self.assertIn(admission.BOM,current)
        self.assertNotIn('PG3976',current)
        for bad in (current,original+original,original.replace('PG3976','PG4432')):
            with self.assertRaisesRegex(ValueError,'one exact prior'):actual.current_guard(bad)
        old=admission.W/'pg4910-current-same-owner-browser-v1'
        for path in ('cases','browser.private.log','manifest.safe.json'):
            self.assertFalse((old/path).exists(),path+' must not represent a completed Browser run')

    def test_composite_preserves_independent_root_capsules_and_entire_chain(self):
        original=root.payload(admission.live(),'a'*64)
        chain={'before':{'history':'old-source-is-data-not-authority'},'after':{},'context':{}}
        raw=composite.compose(original,chain,'b'*64)
        def literal(text,name):return next(ast.literal_eval(n.value) for n in ast.parse(text).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
        joined=literal(raw,'ORACLE')
        inner={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(joined).body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
        self.assertEqual(chain,inner['CHAIN']);self.assertEqual(literal(original,'ORACLE'),inner['ROOT_ORACLE']);self.assertEqual(literal(original,'GUARD'),literal(raw,'GUARD'))
        self.assertIn(root.SLOT+'/before.private.json',joined);self.assertEqual(0,check(raw,'<whole exact Browser chain>'))

    def test_parent18_literal_data_only_and_composite_waits_for_original_exit(self):
        raw=projection.payload('a'*64)
        for text in (admission.SOURCE,admission.BOM,composite.SLOT,"EXPECTED='"+'a'*64+"'",'len(fields)==18'):self.assertIn(text,raw)
        self.assertNotIn('systemctl',raw)
        body=inspect.getsource(composite.previous.main)
        self.assertLess(body.index("'start.safe.json'"),body.index('child.stdin.write'));self.assertIn('child.wait()',body);self.assertNotIn('timeout=',body)
        for path in (ready.__file__,actual.__file__,composite.__file__,projection.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
