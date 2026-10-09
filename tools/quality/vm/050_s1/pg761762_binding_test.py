"""Current Root literal PID1/DONE and foreign/null/duplicate/budget oracle."""
import copy
import unittest
import pg761_capture_done as p
import pg762_a01_current as a
from pg761_current_binding import receipt


class BindingTest(unittest.TestCase):
    def test_current_source_and_original_budget(self):
        raw=p.payload('11111111-2222-4333-8444-555555555555');compile(raw,'<currentDONE>','exec')
        for text in ('2797579','e4093109ab234700b61dd45711126e4e','142602','137240785885',
                     'e64061198bf2aa2716f0895189289db8a9c9dc4741075c22a55c88693ec9879a',
                     '8d4b68b4f1449932ebe506aaf08e584bbfea8dd2','PG750','pg758-fresh-parent-v1','pg761-completed-readonly-v1'):
            self.assertIn(text,raw)
        for old in ('2468821','132812','pg722','PG715'):self.assertNotIn(old,raw)
        for oldrun in ('55ac70e7-0180-4c32-8c91-5a379ebedf24','8633b77f-77dc-4a78-88b4-41165f159b43'):
            with self.assertRaises(AssertionError):p.payload(oldrun)
        compile(p.source(),'<currentmain>','exec')

    def test_current_driver_never_rewrites_baseline(self):
        raw=a.code();compile(raw,'<CurrentA01>','exec')
        for text in ('pg760-retention-post-v1.exit','pg759-observer-v1','PG762-native-a01-v1','PG750',
                     '8d4b68b4f1449932ebe506aaf08e584bbfea8dd2','Current'):self.assertIn(text,raw)
        for old in ('pg722','pg723','pg724','PG726'):self.assertNotIn(old,raw)

    def test_literal_receipt_and_each_foreign(self):
        env={};exec(compile(receipt(),'<dataonly literalPID1>','exec'),env)
        # Independent literal completion at16min; not actualVM receipt.
        rows=[]
        for mid,extra in [('39f53479d3a045ac8e11786248231fbf',{'JOB_ID':'142602','JOB_TYPE':'start','JOB_RESULT':'done'}),('7ad2d189f7e94e70a38c781354912448',{})]:
            rows.append(dict(_BOOT_ID='cc9ed8747f4f450ea1888de1e42c8441',_PID='1',_UID='0',_COMM='systemd',UNIT='schubert-nk-morning-controller.service',INVOCATION_ID='e4093109ab234700b61dd45711126e4e',__MONOTONIC_TIMESTAMP='138200785885',__CURSOR=mid,__REALTIME_TIMESTAMP='1791525500000000',MESSAGE_ID=mid,**extra))
        done=b'NKDONE1\n9de2d03c-28c7-4647-97d9-c66ace06048c\n2026-10-09T05:42:22.532331Z\n021111b4-6de5-4733-917d-5ac176240ffc\n2026-10-09T05:58:20.000000Z\n0\n'
        result=env['completed'](rows,done);self.assertEqual(960,result['elapsedSeconds'])
        for bad in (None,[],rows+[rows[0]]):
            with self.assertRaises(ValueError):env['completed'](bad,done)
        for key,value in (('_PID','2'),('INVOCATION_ID','2aff8ecf3b7d4d15b24a8af0f73a8745'),('JOB_ID','132812'),('__MONOTONIC_TIMESTAMP','139040785886'),('__MONOTONIC_TIMESTAMP','137240785884')):
            bad=copy.deepcopy(rows);bad[0][key]=value
            with self.assertRaises(ValueError):env['completed'](bad,done)
        for bad in (None,done.replace(b'9de2d03c',b'55ac70e7'),done.replace(b'021111b4',b'ab8895ca')):
            with self.assertRaises(ValueError):env['completed'](rows,bad)


if __name__=='__main__':unittest.main()
