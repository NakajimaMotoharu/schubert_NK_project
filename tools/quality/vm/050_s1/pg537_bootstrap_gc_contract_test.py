"""Independent known20-to-GC golden fields, never GC-to-success inference."""
import copy
import unittest
from pg535_bootstrap_contract_test import literal20
from pg535_bootstrap_contract import UNIT
from pg537_bootstrap_gc_contract import current_gc_after_known20, configuration_after_gc, unchanged_after_gc


class GcTest(unittest.TestCase):
    def test_full18_current_gc_requires_complete_real20_and_exact_five_zero_fields(self):
        prior=literal20()
        current={**prior,'InvocationID':'','ExecMainCode':'0','ExecMainStatus':'0',
                 'ExecMainStartTimestampMonotonic':'0','ExecMainExitTimestampMonotonic':'0'}
        self.assertTrue(current_gc_after_known20(prior,current))
        self.assertFalse(current_gc_after_known20(current,current))
        for original,i in ((prior,0),(current,1)):
            for key in original:
                for value in (None,'foreign',0):
                    args=[prior,current];args[i]={**original,key:value}
                    self.assertFalse(current_gc_after_known20(*args))
                bad=dict(original);del bad[key];args=[prior,current];args[i]=bad
                self.assertFalse(current_gc_after_known20(*args))
            for bad in (None,{},[],{**original,'foreign':''}):
                args=[prior,current];args[i]=bad
                self.assertFalse(current_gc_after_known20(*args))
        for key in ('InvocationID','ExecMainCode','ExecMainStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic'):
            self.assertFalse(current_gc_after_known20(prior,{**current,key:prior[key]}))

    def test_sealed_history_and_current_idle_join_preserve_every_other_value(self):
        prior=literal20();gc={**prior,'InvocationID':'','ExecMainCode':'0','ExecMainStatus':'0',
                              'ExecMainStartTimestampMonotonic':'0','ExecMainExitTimestampMonotonic':'0'}
        previous={'User':'schubert-api','ExecStart':'{ path=/usr/bin/java ; argv[]=/usr/bin/java fixed BootstrapAdminMain ; ignore_errors=no ; start_time=[START] ; stop_time=[END] ; pid=42 ; code=exited ; status=20 }'}
        current={'User':'schubert-api','ExecStart':'{ path=/usr/bin/java ; argv[]=/usr/bin/java fixed BootstrapAdminMain ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'}
        actor={'pid':'42','ticks':'123','invocation':'a'*32,'zeroCapabilities':True}
        old={'units':{UNIT:prior,'other.service':{'fixed':'same'}},'configuration':{UNIT:previous,'other.service':{'ExecStart':'same'}},'rows':{'private-fixture':'unchanged'}}
        new=copy.deepcopy(old);new['units'][UNIT]=gc;new['configuration'][UNIT]=current
        self.assertTrue(configuration_after_gc(previous,current,actor))
        self.assertTrue(unchanged_after_gc(old,new,actor))
        for original,replacement in [('path=/usr/bin/java','path=/foreign'),('fixed','foreign'),
                                     ('ignore_errors=no','ignore_errors=yes'),('[n/a]','[OTHER]'),
                                     ('pid=0','pid=42'),('code=(null)','code=exited'),('status=0/0','status=20')]:
            self.assertFalse(configuration_after_gc(previous,{**current,'ExecStart':current['ExecStart'].replace(original,replacement)},actor))
        for i, original in enumerate((old,new,actor)):
            for bad in (None,{},[],{**original,'foreign':True}):
                args=[old,new,actor];args[i]=bad
                self.assertFalse(unchanged_after_gc(*args))
        for key in ('units','configuration','rows'):
            bad=copy.deepcopy(new);bad[key]={}
            self.assertFalse(unchanged_after_gc(old,bad,actor))
        self.assertFalse(unchanged_after_gc(old,new,{**actor,'invocation':'b'*32}))


if __name__=='__main__':
    unittest.main()
