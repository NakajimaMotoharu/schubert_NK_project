import ast
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
from immutable_payload_binding import PROTECTED
from bundle_hash_contract import require_bound
import pg4880_ssc301_302_publication_sources as role
import pg4882_ssc301_302_publication_compile as compiler
import pg4884_ssc301_302_publication_dispatch as dispatch
import pg4886_ssc301_302_publication_post as post


def capsules(raw):
    return Counter(ast.get_source_segment(raw,n) for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in PROTECTED for t in n.targets))


class Publication(unittest.TestCase):
    def test_actual_ro_then_all24_source_roles_and_immutable_capsules(self):
        self.assertTrue(role.qualify()['candidateHostReadonlyVerified'])
        ro=role.ro.sources();values=compiler.generated();self.assertEqual(24,len(values))
        for suffix in ('parent_receipt','warning_parent_projection'):
            self.assertEqual(capsules(ro['pg4872_'+suffix+'.py']),capsules(values['pg4880_'+suffix+'.py']))
        self.assertTrue(require_bound(values['pg4880_native_refs.py'],compiler.ro_compile.sha(compiler.ro_compile.PRIOR/'bundle.safe.json')))
        for value in ('pg4882-frozen-v1.safe.json','pg4866-frozen-v1.safe.json',"('transition','TransitionTest')",'pg4702-release-v1/api/api.jar'):self.assertIn(value,compiler.compiler())
        for name in ('pg1083_cold_publication_contract.py','pg1088_cold_exchange_io.py','pg1090_cold_finite_capture.py','pg2441_ordinary_exchange_io.py'):self.assertIn(name,values)

    def test_foreign_missing_bool_or_unknown_receipt_never_publishes(self):
        original=json.loads((role.W/'pg4878-ssc301-302-ro-independent-post-v1/manifest.safe.json').read_bytes())
        for key,value in [('candidateHostReadonlyVerified',False),('candidateSource',role.CURRENT),('currentSource',role.SOURCE),('candidateManifestSha256','0'*64),('newTenReferencesReturnedNormally',False),('actualExit',False),('native72Preserved',False)]:
            bad=copy.deepcopy(original);bad['result'][key]=value
            with patch.object(role.ro,'qualify'),patch.object(role.json,'loads',return_value=bad),self.subTest(key=key),self.assertRaises(ValueError):role.qualify()

    def test_actual_entry_kind_and_only_finite_actions(self):
        # Pure source-kind fixture, not a forged compile receipt or actual admission.
        fixture={'actualExit':0,'productionSource':role.CURRENT,'candidateSource':role.SOURCE,'candidateManifestSha256':role.BOM,'fileHashes':{n:'a'*64 for n in compiler.generated()}}
        fixture['fileHashes'].update({role.CLASS+'.class':'b'*64,'Pg4880TransitionTest.class':'c'*64})
        dispatch.qualify_fixed(fixture)
        for key,value in [('actualExit',False),('productionSource',role.SOURCE),('candidateSource',role.CURRENT),('candidateManifestSha256','0'*64)]:
            bad=copy.deepcopy(fixture);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):dispatch.qualify_fixed(bad)
        bad=copy.deepcopy(fixture);bad['fileHashes']['Pg4872CandidateRo.class']='0'*64
        with self.assertRaises(ValueError):dispatch.qualify_fixed(bad)
        raw=dispatch.source()
        for marker in ('pg4882-frozen-v1.safe.json','pg4884-stage-v1.exit','0.1.0-PG4702','Pg4880TransitionTest',"['stage'],['activate']",'qualify_fixed(fixed)'):self.assertIn(marker,raw)
        self.assertEqual(1,raw.count('with management_gate('));self.assertIn(dispatch.GUEST,dispatch.STAGE);self.assertIn(dispatch.REMOTE,dispatch.STAGE)
        with patch.object(dispatch.sys,'argv',['tool','start']),patch.object(dispatch,'authenticate_host') as auth,self.assertRaises(ValueError):dispatch.main()
        auth.assert_not_called()

    def test_emitted_independent_all_phase_source_with_explicit_nonruntime_fixture(self):
        original=Path.read_bytes;target=role.W/'pg4882-frozen-v1.safe.json'
        fixture={'actualExit':0,'fileHashes':{'FIXTURE_SOURCE_ONLY':hashlib.sha256(b'fixture').hexdigest()}}
        def read(path):return json.dumps(fixture).encode() if path==target else original(path)
        with patch.object(Path,'read_bytes',read):raw=post.payload()
        self.assertEqual(0,check(raw,'<pure source-only seven-phase emission>'))
        self.assertIn("old_after={**after,'native':expected['native']}",raw)
        for marker in (role.SOURCE,role.BOM,'pg4860-manifest.sig',post.FULL_BEFORE,post.FULL_SHA,'len(phases)>=7',"oracle['PHASES']","for stamp,phase,observed in phases:oracle['verify']",'originalBackupNative72Preserved','oldNativeNotAppliedToNewSource',"'newSourceParentNotStarted':True"):
            self.assertIn(marker,raw)
        t=ast.parse(raw);reader=next(n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name=='read_rows');text=ast.unparse(reader)
        self.assertLess(text.index('sql-read-'),text.index('json.loads(line)'));self.assertLess(text.index('os.fsync(fd)'),text.index('json.loads(line)'))
        owned=next(n for n in t.body if isinstance(n,ast.Try) and 'UnrefUnit' in ast.unparse(n.finalbody));self.assertGreater(t.body[-1].lineno,owned.end_lineno)
        for path in (role.__file__,compiler.__file__,dispatch.__file__,post.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
