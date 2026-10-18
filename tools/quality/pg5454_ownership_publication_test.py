import ast
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
from bundle_hash_contract import require_bound
from pg5444_ownership_unused_post_test import capsules
import pg5454_ownership_publication_sources as role
import pg5456_ownership_publication_compile as compiler
import pg5458_ownership_publication_dispatch as dispatch
import pg5460_ownership_publication_post as post


class Publication(unittest.TestCase):
    def test_genuine_ro_full24_capsules_bundle_and_actual_A2_ABI(self):
        self.assertTrue(role.qualify()['native88Preserved'])
        before,values=role.ro.sources(),compiler.generated();self.assertEqual(len(values),24)
        for suffix in('parent_receipt','warning_parent_projection'):
            self.assertEqual(capsules(before['pg5446_'+suffix+'.py']),capsules(values['pg5454_'+suffix+'.py']))
        self.assertTrue(require_bound(values['pg5454_native_refs.py'],compiler.ro_compile.sha(compiler.ro_compile.PRIOR/'bundle.safe.json')))
        for marker in('pg5456-frozen-v1.safe.json','pg5440-frozen-v1.safe.json',"('transition','TransitionTest')",'pg4980-release-v1/api/api.jar'):
            self.assertIn(marker,compiler.compiler())
        for name in('pg1083_cold_publication_contract.py','pg1088_cold_exchange_io.py','pg1090_cold_finite_capture.py','pg2441_ordinary_exchange_io.py'):
            self.assertIn(name,values)

    def test_foreign_source_old_native_unknown_reference_or_bool_rejected(self):
        original=json.loads((role.W/role.ro_post.SLOT/'manifest.safe.json').read_bytes())
        for key,value in(('candidateHostReadonlyVerified',False),('candidateSource',role.CURRENT),('currentSource',role.SOURCE),('native88Preserved',False),('newTenReferencesReturnedNormally',False),('actualExit',False)):
            bad=copy.deepcopy(original);bad['result'][key]=value
            with self.subTest(key=key),patch.object(role.ro,'qualify'),patch.object(role.json,'loads',return_value=bad),self.assertRaises(ValueError):role.qualify()

    def test_exact_finite_class_kind_fresh_stage_contract_single_gate(self):
        fixed={'actualExit':0,'productionSource':role.CURRENT,'candidateSource':role.SOURCE,'candidateManifestSha256':role.BOM,
            'fileHashes':{name:'a'*64 for name in compiler.generated()}}
        fixed['fileHashes'].update({role.CLASS+'.class':'b'*64,'Pg5454TransitionTest.class':'c'*64})
        dispatch.qualify_fixed(fixed)
        for key,value in(('actualExit',False),('productionSource',role.SOURCE),('candidateSource',role.CURRENT)):
            with self.assertRaises(ValueError):dispatch.qualify_fixed({**fixed,key:value})
        bad=copy.deepcopy(fixed);bad['fileHashes']['Pg5446CandidateRo.class']='0'*64
        with self.assertRaises(ValueError):dispatch.qualify_fixed(bad)
        raw=dispatch.source()
        for marker in('pg5456-frozen-v1.safe.json','pg5458-stage-v1.exit','0.1.0-PG4980','Pg5454TransitionTest','qualify_fixed(fixed)'):
            self.assertIn(marker,raw)
        self.assertEqual(raw.count('with management_gate('),1)
        self.assertIn(dispatch.GUEST,dispatch.STAGE);self.assertIn(dispatch.REMOTE,dispatch.STAGE)
        self.assertIn('/pg5454-ownership-publication-tools-v1.tar',dispatch.STAGE)
        for old in('0.1.0-PG4860','pg5008','pg5012','pg5000'):self.assertNotIn(old,dispatch.STAGE)
        with patch.object(dispatch.sys,'argv',['tool','start']),patch.object(dispatch,'authenticate_host')as auth,self.assertRaises(ValueError):dispatch.main()
        auth.assert_not_called()

    def test_independent_allphase_fixture_sql_durable_before_parse_and_true_refs(self):
        original=Path.read_bytes;target=role.W/'pg5456-frozen-v1.safe.json'
        fixture={'actualExit':0,'fileHashes':{'FIXTURE_SOURCE_ONLY':hashlib.sha256(b'independent fixture').hexdigest()}}
        def read(path):return json.dumps(fixture).encode()if path==target else original(path)
        with patch.object(Path,'read_bytes',read):raw=post.payload()
        self.assertEqual(check(raw,'<nonruntime independent finite source fixture>'),0)
        for marker in(role.SOURCE,role.BOM,'pg5430-manifest.sig',post.FULL_BEFORE,post.FULL_SHA,
            "old_after={**after,'native':expected['native']}",'len(phases)>=7',"oracle['PHASES']",
            "for stamp,phase,observed in phases:oracle['verify']",'originalBackupNative88Preserved','oldNativeNotAppliedToNewSource',"'newSourceParentNotStarted':True"):
            self.assertIn(marker,raw)
        tree=ast.parse(raw);reader=next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='read_rows');body=ast.unparse(reader)
        self.assertLess(body.index('sql-read-'),body.index('json.loads(line)'));self.assertLess(body.index('os.fsync(fd)'),body.index('json.loads(line)'))
        held=next(n for n in tree.body if isinstance(n,ast.Try)and 'UnrefUnit'in ast.unparse(n.finalbody))
        self.assertGreater(tree.body[-1].lineno,held.end_lineno)
        for item in(role,compiler,dispatch,post):self.assertEqual(checkPath(item.__file__),0)
        self.assertEqual(checkPath(__file__),0)


if __name__=='__main__':unittest.main()
