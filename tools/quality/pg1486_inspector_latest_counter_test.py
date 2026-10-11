"""Independent manifest contract, null/unknown/foreign/false and bool-zero rejection."""
import copy
import unittest
from pg1486_inspector_latest_counter import qualified_inspector,SOURCE

class CounterContractTest(unittest.TestCase):
    def fixture(self):return {'actualExit':0,'productionSource':SOURCE,'classByteMismatch':0,'terminalRetainedNotSelected':True,'sameSessionUnion0':True,'closingOracle':{'sameSession':True,'probeMonotonic':True,'latestClosingOnly':True}}
    def test_complete_handwritten_contract(self):self.assertIsNone(qualified_inspector(self.fixture()))
    def test_false_foreign_missing_and_bool_zero(self):
        for key,value in [('actualExit',1),('actualExit',False),('productionSource','foreign'),('classByteMismatch',1),('classByteMismatch',False),('terminalRetainedNotSelected',False),('sameSessionUnion0',False),('closingOracle',None)]:
            with self.subTest(key=key,value=value):
                v=self.fixture();v[key]=value
                with self.assertRaises(ValueError):qualified_inspector(v)
        for key in self.fixture():
            v=self.fixture();del v[key]
            with self.assertRaises(ValueError):qualified_inspector(v)
        for key in ('sameSession','probeMonotonic','latestClosingOnly'):
            v=copy.deepcopy(self.fixture());v['closingOracle'][key]=False
            with self.assertRaises(ValueError):qualified_inspector(v)
        for v in (None,[],{}):
            with self.assertRaises(ValueError):qualified_inspector(v)

if __name__=='__main__':unittest.main()
