"""Independent failed PID1/done vectors, including false normal and foreign generations."""
import copy
import unittest
import pg4304_current_failed_parent_contract as c


def fixture():
    b={'boot':c.BOOT.replace('-',''),'invocation':'1'*32,'job':'17','start':1000000,'run':'11111111-1111-4111-8111-111111111111',
       'cutoff':'2026-10-16T11:32:53Z','activation':'22222222-2222-4222-8222-222222222222','rootPid':123}
    state={'Id':c.UNIT,'LoadState':'loaded','ActiveState':'failed','SubState':'failed','InvocationID':b['invocation'],'MainPID':'0','ControlPID':'0','Job':'',
           'Result':'timeout','ExecMainCode':'1','ExecMainStatus':'143','ExecMainStartTimestampMonotonic':'1000000','ExecMainExitTimestampMonotonic':'1801072841'}
    common={'UNIT':c.UNIT,'INVOCATION_ID':b['invocation'],'_PID':'1','_UID':'0','_BOOT_ID':b['boot'],'JOB_ID':'17','JOB_TYPE':'start'}
    rows=[{**common,'MESSAGE_ID':'7d4958e842da4a758f6c1cdc7b36dcc5','__MONOTONIC_TIMESTAMP':'1000100'},
          {**common,'MESSAGE_ID':'be02cf6855d2428ba40df7e9d022f03d','JOB_RESULT':'failed','__MONOTONIC_TIMESTAMP':'1801072941'}]
    done=('NKDONE1\n'+b['run']+'\n'+b['cutoff']+'\n'+b['activation']+'\n2026-10-16T12:00:00Z\n10\n').encode()
    return b,state,rows,done


class FailedTest(unittest.TestCase):
    def test_independent_timeout_is_not_warning_normal_receipt(self):
        b,s,r,d=fixture();v=c.classify(c.SOURCE,c.BOM,c.BOOT,b,s,r,d)
        self.assertEqual(v['elapsedSeconds'],1800.072841);self.assertEqual(v['doneCodeDataOnly'],10)
        for k in ['parentNormal','genuineRootDone','normalUnit0or10','recoveryAuthorityIssued','stopAuthority','formalAccepted']:self.assertIs(v[k],False)
        self.assertTrue(v['actualPid1StartFailed'])

    def test_missing_null_foreign_state_and_binding_refused(self):
        b,s,r,d=fixture()
        for which,value in [('binding',b),('state',s)]:
            for key in value:
                for bad in [None,'foreign',False]:
                    v=copy.deepcopy(value);v[key]=bad
                    with self.subTest(which=which,key=key,bad=bad),self.assertRaises(ValueError):c.classify(c.SOURCE,c.BOM,c.BOOT,v if which=='binding'else b,v if which=='state'else s,r,d)
                v=copy.deepcopy(value);del v[key]
                with self.assertRaises(ValueError):c.classify(c.SOURCE,c.BOM,c.BOOT,v if which=='binding'else b,v if which=='state'else s,r,d)
        for source,bom,boot in [(None,c.BOM,c.BOOT),(c.SOURCE,'f'*64,c.BOOT),(c.SOURCE,c.BOM,'foreign')]:
            with self.assertRaises(ValueError):c.classify(source,bom,boot,b,s,r,d)

    def test_journal_and_done_malformed_or_normalization_refused(self):
        b,s,r,d=fixture()
        for rows in [None,[],r[:1],r+r,r[::-1]+r[:1],[{**r[0],'_PID':'123'},r[1]],[r[0],{**r[1],'JOB_RESULT':'done'}],[r[0],{**r[1],'__MONOTONIC_TIMESTAMP':'01801072941'}]]:
            with self.subTest(rows=type(rows)),self.assertRaises(ValueError):c.classify(c.SOURCE,c.BOM,c.BOOT,b,s,rows,d)
        for done in [None,b'',d[:-1],d.replace(b'\n',b'\r\n'),d.replace(b'NKDONE1',b'UNKNOWN'),d.replace(b'\n10\n',b'\n143\n'),d.replace(b'2026-10-16T12:00:00Z',b'2026-10-16T13:00:00Z'),b'\xff\n']:
            with self.subTest(done=type(done)),self.assertRaises(ValueError):c.classify(c.SOURCE,c.BOM,c.BOOT,b,s,r,done)


if __name__=='__main__':unittest.main()
