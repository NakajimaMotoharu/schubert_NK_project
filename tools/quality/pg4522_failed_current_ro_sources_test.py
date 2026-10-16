"""Fresh failed-data/new candidate oracle; old successful tuple cannot qualify."""
import ast
import copy
import json
import unittest
import pg4522_failed_current_ro_sources as r


class FailedCurrentRo(unittest.TestCase):
    def test_actual_unused_full_post_and_all_required_flags(self):
        v=json.loads((r.W/'pg4520-failed-current-unused-post-v1/manifest.safe.json').read_bytes());self.assertEqual(v['result'],r.qualify_result(v))
        for key in v['result']:
            if key in ['profile','javaSha256','compileSha256','observedUTC','candidateFileInventory','authorityOrCoverageClaim','ordinaryPoolsFreshSocketMatched','independentFailedDoneRecoveryPost','nativeQualificationPending','signalStartStopReloadDbWrites','formalAccepted']:continue
            bad=copy.deepcopy(v);bad['result'][key]=None
            with self.subTest(key=key),self.assertRaises(ValueError):r.qualify_result(bad)
        for key,value in [('currentSource',r.SOURCE),('candidateSource',r.CURRENT),('actualExit',False)]:
            bad=copy.deepcopy(v);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):r.qualify_result(bad)
        for key,value in [('formalAccepted',True),('signalStartStopReloadDbWrites',False),('oldParentNormal',True),('candidateNativeCredit',True)]:
            bad=copy.deepcopy(v);bad['result'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):r.qualify_result(bad)

    def test_all18_new_failed_parent_role_and_literal19_not_old_normal_authority(self):
        v=r.sources();self.assertEqual(18,len(v));self.assertIn('Pg4522CandidateRo.java',v)
        java=v['Pg4522CandidateRo.java'];self.assertIn('StartupPermitRecords.State.INVALID && epoch.permitDigest().isEmpty()',java)
        self.assertIn('b1ba37cb-9b2b-469b-a5f2-b0e6d8c97cd1',java);self.assertNotIn('f29290f8-69ed-49fe-9f2f-33b4efdea422',java)
        self.assertIn('genuineParentNormalWarningOriginal=false\\ncurrentManagerGc=false\\nfailedParent143DataOnly=true',java)
        native=v['pg4522_native_refs.py'];self.assertIn('failed_completed(rows, done)',native);self.assertIn("INV = 'bbcdb69957764d489a9c757b441542fd'",native)
        self.assertNotIn('qualify_warning_parent',native);self.assertNotIn("'/proc/225062'",native)
        tree=ast.parse(native);binding=next(n for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='FIELDS'for x in ast.walk(n.targets[0])))
        ns={'sealed':{'UNITS':[]}};exec(compile(ast.Module(body=[binding],type_ignores=[]),'<actual full RO field binding>','exec'),ns)
        literal={'Id','LoadState','ActiveState','SubState','MainPID','ControlPID','Job','InvocationID','ControlGroup','Result','ExecMainCode','ExecMainStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic','Type','KillMode','SendSIGKILL','RemainAfterExit','Restart'}
        self.assertEqual(literal,ns['FIELDS']);self.assertIs(set,type(ns['FIELDS']))


if __name__=='__main__':unittest.main()
