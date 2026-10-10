import ast
import datetime
import unittest
from pg1241_fresh_inspector_provenance import PAYLOAD

class IndependentInboxOracleTest(unittest.TestCase):
    def test_actual_ss_time_state_boundary_null_and_unknown_oracle(self):
        t=ast.parse(PAYLOAD);compile(PAYLOAD,'<actual Inspector qualification>','exec')
        ns={'datetime':datetime}
        nodes=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name in {'require','eligible_rows'}]
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual independent predicate>','exec'),ns)
        cutoff=datetime.datetime(2026,10,10,20,3,22,718197,tzinfo=datetime.timezone.utc)
        rows=[{'processing_state':state,'expires_at':(cutoff+datetime.timedelta(microseconds=delta)).isoformat()}for state in ['PROCESSING','COMPLETED','ERROR']for delta in [-1,0,1]]
        self.assertEqual(ns['eligible_rows'](rows,cutoff),[rows[3],rows[6]])
        for bad in [None,[None],[{}],[{'processing_state':'UNKNOWN','expires_at':cutoff.isoformat()}],[{'processing_state':'COMPLETED','expires_at':None}]]:
            with self.assertRaises(ValueError):ns['eligible_rows'](bad,cutoff)
        with self.assertRaises(ValueError):ns['eligible_rows'](rows,cutoff.replace(tzinfo=None))
        self.assertFalse('maintenance_next_inbox('in PAYLOAD)
        self.assertTrue('classSessionCounterQualificationPending'in PAYLOAD)

if __name__=='__main__':unittest.main()
