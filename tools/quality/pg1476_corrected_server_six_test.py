import unittest
from pg1476_corrected_server_six import server_source


class CorrectedFullSourceTest(unittest.TestCase):
    def test_only_current_snapshot_and_new_totals_no_vm_mutation(self):
        raw=server_source('a'*40,'b'*64);ns={'__name__':'fixed_compile_only'};exec(compile(raw,'<fixed server>','exec'),ns)
        good=[0,True,[],3578,523,1635]
        self.assertTrue(ns['complete_result'](*good))
        for at,values in {0:[143,1,None,True],1:[False,None,1],2:[None,['failed']],3:[3576,3577,3579],4:[522,524],5:[1634,1636]}.items():
            for value in values:
                args=good.copy();args[at]=value;self.assertFalse(ns['complete_result'](*args))
        for text in ['PG1476-source.tar','SCHUBERT_SHELLCHECK','SCHUBERT_PG_ROOT','umask=0o027','a'*40,'b'*64]:self.assertIn(text,raw)
        for text in ['2c29d7a17a5eca2f61b24e99af13260a3c286a09','3576','systemctl','StartUnit','StopUnit']:self.assertNotIn(text,raw)

    def test_missing_or_wrong_identity_is_rejected(self):
        for args in [(None,'b'*64),('a'*39,'b'*64),('a'*40,'z'*64),('A'*40,'b'*64)]:
            with self.assertRaises(ValueError):server_source(*args)


if __name__=='__main__':unittest.main()
