"""Actual finite entry receipt/kind checks and independent seven-phase durable post."""
import ast
import copy
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4726_ssc299_publication_dispatch as dispatch
import pg4728_ssc299_publication_post as post


class PublicationAction(unittest.TestCase):
    def test_actual_entry_receipt_kind_and_only_finite_actions(self):
        fixed=json.loads((dispatch.role.W/'pg4724-frozen-v1.safe.json').read_bytes())
        dispatch.qualify_fixed(fixed)
        for key,value in [('actualExit',False),('productionSource',dispatch.role.SOURCE),
                          ('candidateSource',dispatch.role.CURRENT),('candidateManifestSha256','0'*64)]:
            bad=copy.deepcopy(fixed);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):dispatch.qualify_fixed(bad)
        bad=copy.deepcopy(fixed);bad['fileHashes']['Pg4714CandidateRo.class']='0'*64
        with self.assertRaises(ValueError):dispatch.qualify_fixed(bad)
        raw=dispatch.source()
        for value in ['pg4724-frozen-v1.safe.json','pg4726-stage-v1.exit','0.1.0-PG4432',
                      'Pg4722TransitionTest',"['stage'],['activate']",'qualify_fixed(fixed)']:
            self.assertIn(value,raw)
        self.assertEqual(1,raw.count('with management_gate('))
        self.assertIn(dispatch.GUEST,dispatch.STAGE);self.assertIn(dispatch.REMOTE,dispatch.STAGE)
        self.assertNotIn('systemctl start',raw);self.assertNotIn('--resume',raw)
        with patch.object(dispatch.sys,'argv',['tool','start']),patch.object(dispatch,'authenticate_host')as auth:
            with self.assertRaises(ValueError):dispatch.main()
            auth.assert_not_called()

    def test_new_source_reader_old_native_data_and_every_phase_not_just_final(self):
        raw=post.payload();self.assertEqual(0,check(raw,'<actual independent finite post>'))
        self.assertIn(post.role.SOURCE,raw);self.assertIn(post.role.BOM,raw)
        self.assertIn('pg4702-manifest.sig',raw);self.assertIn(post.FULL_BEFORE,raw)
        self.assertIn(post.FULL_SHA,raw)
        for value in ['len(phases)>=7','oracle[\'PHASES\']',"for stamp,phase,observed in phases:oracle['verify']",'oldNativeNotAppliedToNewSource',"'newSourceParentNotStarted':True"]:
            self.assertIn(value,raw)
        tree=ast.parse(raw);reader=next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='read_rows')
        text=ast.unparse(reader)
        self.assertLess(text.index('sql-read-'),text.index('json.loads(line)'))
        self.assertLess(text.index('os.fsync(fd)'),text.index('json.loads(line)'))
        owned=next(n for n in tree.body if isinstance(n,ast.Try)and 'UnrefUnit' in ast.unparse(n.finalbody))
        final=next(n for n in tree.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and ast.unparse(n.value.func)=='print')
        self.assertGreater(final.lineno,owned.end_lineno)
        for path in [dispatch.__file__,post.__file__,__file__]:self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
