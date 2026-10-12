import copy
import re
import unittest
from pg1510_publication_gc_bridge import ORDER,FIELDS,GC,normalize,unit_kind

def parse(v):
    if type(v)is not str:return None
    m=re.fullmatch(r'([^|]+)\|([^|]+)\|(yes|no)\|([^|]+)\|([^|]+)\|([0-9]+)\|([^|]+)\|([^|]+)',v)
    return m.groups()if m else None

class GCBridgeTest(unittest.TestCase):
    def fixture(self):
        units={};cfg={}
        for name in ORDER:
            units[name]={k:'fixed'for k in FIELDS};units[name].update(Id=name,ActiveState='inactive',SubState='dead',Result='success',MainPID='0',ControlPID='0',Job='',InvocationID='a'*32,ExecMainStartTimestampMonotonic='10',ExecMainExitTimestampMonotonic='20',ExecMainCode='1',ExecMainStatus='143'if name=='artemis.service'else'0')
            cfg[name]={f'fixed{k}':'same'for k in range(31)};cfg[name]['ExecStart']='/fixed|/fixed argv|no|old-start|old-stop|42|exited|143'
        return {'units':units,'configuration':cfg,'rows':{'fixedTable':[{'state':'kept'}]},'epoch':'INVALID','permit':'kept','native':'kept','original':'kept'}
    def test_warm_and_strict_gc_preserve_real_history(self):
        expected=self.fixture();self.assertTrue(all(v=='WARM'for v in normalize(expected,copy.deepcopy(expected),parse)[1].values()))
        current=copy.deepcopy(expected)
        for name in ORDER:
            current['units'][name].update(GC);current['configuration'][name]['ExecStart']='/fixed|/fixed argv|no|n/a|n/a|0|(null)|0/0'
        result,kinds=normalize(expected,current,parse);self.assertEqual(expected,result);self.assertTrue(all(v=='STRICT_GC'for v in kinds.values()))
        for name in ORDER:
            for key in FIELDS:
                bad=copy.deepcopy(current);bad['units'][name][key]='foreign'
                with self.assertRaises(ValueError):normalize(expected,bad,parse)
            for key in current['configuration'][name]:
                bad=copy.deepcopy(current);bad['configuration'][name][key]='foreign'
                with self.assertRaises(ValueError):normalize(expected,bad,parse)
        for key in ('rows','epoch','permit','native','original'):
            bad=copy.deepcopy(current);bad[key]='changed'
            with self.assertRaises(ValueError):normalize(expected,bad,parse)
    def test_cold_zero_does_not_prove_warm_stop_missing_null_rejected(self):
        a=self.fixture()['units'][ORDER[0]];b=copy.deepcopy(a);b.update(GC)
        with self.assertRaises(ValueError):unit_kind(b,b)
        for x in (None,{},[],{'Id':'foreign'}):
            with self.assertRaises(ValueError):unit_kind(a,x)

if __name__=='__main__':unittest.main()
