"""Typed original result and all completion dependencies remain independent."""
import copy
import unittest
import pg4494_inspect_pair_recover as entry


class RecoveryReceipt(unittest.TestCase):
    def fixture(self):
        post={'actualExit':0,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','BOM':'0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab',
          'newMARDDBTenRefNormalClose':True,'all24OriginalBackupNativeUnitConfigUnchanged':True,'oldParentNormal':False,'parent143StillFailed':True,'independentFailedDoneRecoveryPost':True,
          'signalStartStopReloadDbWrites':0,'formalAccepted':False}
        return {'actualExit':0,'source':post['source'],'BOM':post['BOM'],'boot':'79a3260a-e16d-42bf-942a-b914ed144c28','mode':'recover',
          'oldScopesNormal':False,'newTenRefsNormalClose':True,'unitOperationsIssued':0,'candidatePlaced':False,'formalAccepted':False,'allOldProcessesAndResourcesGone':True,
          'signalsIssued':2,'independentPost':post}

    def test_literal_full_dependency_and_natural_python_terminal(self):
        self.assertEqual(self.fixture(),entry.complete(self.fixture()))
        v=self.fixture();v['signalsIssued']=1;self.assertEqual(1,entry.complete(v)['signalsIssued'])

    def test_every_top_and_post_dependency_must_be_typed_and_present(self):
        for level in ['outer','post']:
            v=self.fixture();keys=list(v if level=='outer'else v['independentPost'])
            for key in keys:
                bad=copy.deepcopy(v);target=bad if level=='outer'else bad['independentPost'];del target[key]
                with self.subTest(level=level,key=key),self.assertRaises(ValueError):entry.complete(bad)
            for key in ['actualExit','formalAccepted']:
                bad=copy.deepcopy(v);target=bad if level=='outer'else bad['independentPost'];target[key]=False if key=='actualExit'else 0
                with self.subTest(level=level,key=key),self.assertRaises(ValueError):entry.complete(bad)

    def test_old_success_wrong_source_and_extra_signals_do_not_close(self):
        for key,value in [('signalsIssued',0),('signalsIssued',3),('signalsIssued',True),('oldScopesNormal',True),('source','964e96e45bb588e7e75798b5adf425cbd9985427')]:
            v=self.fixture();v[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):entry.complete(v)


if __name__=='__main__':unittest.main()
