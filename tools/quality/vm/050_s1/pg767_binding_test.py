"""Current source/postqualifier stricttype and readonly nineprivate join literals."""
import copy
import unittest
from pg767_current_baseline import source


def fixture():
    return {'actualExit':0,'proofHashes':{'after.private.json':{'sha256':'1'*64}},
        **{key:True for key in ('all24UnchangedTwice','allTenUnitsKernelEmpty','allActorGone','allClientAdvisoryFlock0','whole187SignedArtifactBytesVerified')}}


class Test(unittest.TestCase):
    def test_exact_new_current_and_allnine(self):
        raw=source(fixture());compile(raw,'<noVM>','exec')
        for v in ('pg764-native-stop-v1','pg765-terminal-final-v1.exit','pg767-completed-baseline-v1',
            '8d4b68b4f1449932ebe506aaf08e584bbfea8dd2','0.1.0-PG750','e4093109ab234700b61dd45711126e4e',"'batchRows':544",'1'*64):self.assertIn(v,raw)
        for cohort in ('664','702','737'):
            for kind in ('tools','verify','existing'):self.assertIn('pg'+cohort+'-bootstrap-'+kind+'-v1',raw)
        for bad in ('systemctl start','systemctl stop','DELETE FROM','os.unlink(','os.replace(','pg728','pg729','PG715'):self.assertNotIn(bad,raw)

    def test_no_false_missing_or_foreign_success(self):
        for value in (True,False,None,'0',0.0,1):
            bad=fixture();bad['actualExit']=value
            with self.assertRaises(AssertionError):source(bad)
        for key in fixture().keys()-{'actualExit','proofHashes'}:
            for value in (False,1,None):
                bad=fixture();bad[key]=value
                with self.assertRaises(AssertionError):source(bad)
        for value in (None,'notsha','a'*63,'F'*64):
            bad=copy.deepcopy(fixture());bad['proofHashes']['after.private.json']['sha256']=value
            with self.assertRaises(AssertionError):source(bad)


if __name__=='__main__':unittest.main()
