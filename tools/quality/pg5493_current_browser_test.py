"""Identity-only Browser and complete newday Root/Browser chain invariants; no real Browser mutation."""
import ast
import inspect
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg5045_current_browser_socks as socks
import pg5476_current_admission_image as admission
import pg5482_current_newday_whole_seal as root
import pg5486_current_browser_ready as ready
import pg5488_current_same_owner_browser as actual
import pg5490_current_browser_composite as composite
import pg5492_current_parent_projection as projection


def literal(raw,name):
    return next(ast.literal_eval(n.value)for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets))


class Browser(unittest.TestCase):
    def test_original_twelve_oracles_unchanged_except_source_identity(self):
        self.assertEqual(ready.SOURCE,admission.SOURCE);self.assertIn('tools/quality/pg5486_current_browser_ready.py',ready.PINNED)
        for name in ready.shared.JAVA_INPUTS:
            raw=(ready.shared.ROOT/name).read_text()
            if name not in ready.shared.SHARED:
                self.assertEqual(raw.count(ready.shared.OLD),1);bound=raw.replace(ready.shared.OLD,ready.SOURCE)
                self.assertEqual(bound.replace(ready.SOURCE,ready.shared.OLD),raw)
        self.assertIn("['plannedCases']==12",inspect.getsource(ready.shared.require_ready))

    def test_no_browser_without_genuine_current_and_owned_socks(self):
        with patch.object(actual,'receipt',side_effect=ValueError('same296 proof missing')),self.assertRaisesRegex(ValueError,'same296 proof missing'):actual.guard()
        template=actual.previous.previous.previous.previous
        body=inspect.getsource(template.main)
        self.assertLess(body.index('ready.require_ready()'),body.index('subprocess.run(command,'))
        self.assertIn("raw.replace('previous.previous.owned_socks()', 'owned_socks()')",inspect.getsource(actual.previous.main))
        self.assertNotIn('owner.EXPECTED=',inspect.getsource(socks))

    def test_numeric_same_source_receipts_only(self):
        good={'actualExit':0,'source':admission.SOURCE,'result':{'literal':'independent'}}
        with patch.object(actual.json,'loads',return_value=good),patch.object(actual.admission.W.__class__,'read_bytes',return_value=b'fixture'):
            self.assertEqual(actual.receipt('purefixture')['literal'],'independent')
        for key,value in(('actualExit',False),('actualExit',1),('source',admission.previous.SOURCE),('result',None)):
            with patch.object(actual.json,'loads',return_value={**good,key:value}),patch.object(actual.admission.W.__class__,'read_bytes',return_value=b'fixture'),self.assertRaises(ValueError):actual.receipt('purefixture')

    def test_exactly_one_release_authority_not_history_rewrite(self):
        original='before\n/opt/schubert-nk/releases/0.1.0-PG3976\nafter';bound=actual.current_guard(original)
        self.assertEqual(bound,original.replace('PG3976','PG5430'))
        for bad in(bound,original+original,original.replace('PG3976','PG4980')):
            with self.assertRaises(ValueError):actual.current_guard(bad)

    def test_composite_preserves_full_current_root_guard_oracle_and_history_chain(self):
        original=root.payload(admission.live(),'a'*64);chain={'before':{'history':'old-source-is-data-only'},'after':{},'context':{}}
        raw=composite.compose(original,chain,'b'*64);joined=literal(raw,'ORACLE')
        inner={n.targets[0].id:ast.literal_eval(n.value)for n in ast.parse(joined).body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
        self.assertEqual(inner['CHAIN'],chain);self.assertEqual(inner['ROOT_ORACLE'],literal(original,'ORACLE'))
        self.assertEqual(literal(raw,'GUARD'),literal(original,'GUARD'));self.assertIn('def qualify_new_day',inner['ROOT_ORACLE'])
        self.assertIn(root.SLOT+'/before.private.json',joined);self.assertEqual(check(raw,'<same296 whole Browser chain>'),0)

    def test_parent18_data_and_original_composite_child_wait(self):
        raw=projection.payload('a'*64)
        for marker in(admission.SOURCE,admission.BOM,composite.SLOT,"EXPECTED='"+'a'*64+"'",'len(fields)==18'):self.assertIn(marker,raw)
        self.assertNotIn('systemctl',raw)
        body=inspect.getsource(composite.previous.previous.previous.main)
        self.assertLess(body.index("'start.safe.json'"),body.index('child.stdin.write'));self.assertIn('child.wait()',body);self.assertNotIn('timeout=',body)
        for item in(socks,ready,actual,composite,projection):self.assertEqual(checkPath(item.__file__),0)
        self.assertEqual(checkPath(__file__),0)


if __name__=='__main__':unittest.main()
