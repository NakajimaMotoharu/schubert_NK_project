"""Independent clock/error/history vectors; never contact the VM or launch Browser."""
import copy
import inspect
import unittest
from pyflakes.api import check,checkPath
import pg5520_guest_clock_contract as clock
from pg5520_guest_clock_contract_test import context
from pg3136_browser_rows_oracle_test import fixture
import pg5522_guest_clock_browser_ready as ready
import pg5524_guest_clock_same_owner_browser as actual
import pg5526_guest_clock_browser_composite as entry
import pg5528_guest_clock_parent_projection as projection


class Chain(unittest.TestCase):
    def test_failed_time_criterion_never_normalized_or_row_derived(self):
        before,after=fixture();c=context();c['lower']=c['lowerClock']['instant']='2026-10-15T02:03:00Z'
        c['upper']=c['upperClock']['instant']='2026-10-15T02:04:00Z'
        old={'before':before,'after':after,'context':{'owner':1,'lower':'2026-10-15T02:00:05Z','upper':'2026-10-15T02:02:05Z'}}
        chain={'before':after,'after':{},'context':c}
        result=entry.preserved_prefix(old,chain,'2026-10-15T01:59:00Z')
        self.assertEqual(result['originalFailedContext'],old['context']);self.assertFalse(result['oldFiniteTimeWindowQualified']);self.assertFalse(result['failedCaseNormalized'])
        self.assertEqual(result['context']['lower'],'2026-10-15T01:59:00Z');self.assertEqual(result['context']['upper'],c['lower'])
        # Exact effects, owner, independent anchor, and captured-clock integrity.
        for kind in('gap','owner','anchor','host'):
            x,y=copy.deepcopy(old),copy.deepcopy(chain);anchor='2026-10-15T01:59:00Z'
            if kind=='gap':y['before']={}
            elif kind=='owner':x['context']['owner']=2
            elif kind=='anchor':anchor='2026-10-15T02:05:00Z'
            else:y['context'].pop('lowerClock')
            with self.subTest(kind=kind),self.assertRaises(ValueError):entry.preserved_prefix(x,y,anchor)

    def test_composite_preserves_root_guard_oracle_and_all_snapshots(self):
        raw=entry.root.payload(entry.admission.live(),'a'*64)
        before,after=fixture();chain={'before':after,'after':{'history':'literal source-is-data'},'context':context()}
        prefix={'kind':'FAILED_HOST_CLOCK_BROWSER','before':before,'after':after,'context':{},'originalFailedContext':{'literal':'immutable'},'oldBrowserActualExit':1,'oldFiniteTimeWindowQualified':False,'failedCaseNormalized':False}
        result=entry.compose(raw,chain,'b'*64,prefix);oracle=entry.literal(result,'ORACLE')
        self.assertEqual(entry.literal(result,'GUARD'),entry.literal(raw,'GUARD'));self.assertEqual(entry.literal(oracle,'ROOT_ORACLE'),entry.literal(raw,'ORACLE'))
        self.assertEqual(entry.literal(oracle,'CHAIN'),chain);self.assertEqual(entry.literal(oracle,'PARTIAL_CHAIN'),[prefix]);self.assertIn('oldFiniteTimeWindowQualified',oracle)
        self.assertIn(entry.root.SLOT+'/before.private.json',oracle);self.assertIn(entry.SLOT,result);self.assertEqual(check(result,'<new guest clock failed-prefix chain>'),0)
        ns={};exec(compile(entry.literal(oracle,'PARTIAL_ORACLES')['FAILED_HOST_CLOCK_BROWSER'],'<independent partial effects>','exec'),ns)
        partial=ns['qualify'](before,after,1,'2026-10-15T02:00:00Z','2026-10-15T02:02:00Z')
        self.assertTrue(partial['all24PartialQualified']);self.assertFalse(partial['oldFiniteTimeWindowQualified']);self.assertNotIn('all24Qualified',partial)

    def test_new_driver_and_ready_are_new_only_and_use_strict_post(self):
        raw=actual.entry_source();compile(raw,'<new coherent guest clock Browser>','exec')
        self.assertIn('pg5520_guest_clock_contract.py',raw);self.assertNotIn('pg3136_browser_rows_oracle.py',raw)
        self.assertIn('guestClockQualified',raw);self.assertIn('rootReplayed=False',raw)
        self.assertEqual(len(ready.namespace()['ORACLES']),3)
        self.assertIn('pg5522_guest_clock_browser_ready.py',' '.join(ready.PINNED))
        self.assertIn(entry.SLOT,projection.payload('a'*64));self.assertNotIn('systemctl',projection.payload('a'*64))
        self.assertIn("old_proof['phaseExits']==[0,1]",inspect.getsource(entry.payload))
        for item in(clock,ready,actual,entry,projection):self.assertEqual(checkPath(item.__file__),0)
        self.assertEqual(checkPath(__file__),0)


if __name__=='__main__':unittest.main()
