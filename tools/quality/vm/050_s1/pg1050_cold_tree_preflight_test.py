"""PT-DEP-1050001..003 fixed exclusion/source/side-effect boundary of preflight."""
import ast
import unittest
from pg1050_cold_tree_preflight import payload


class Preflight(unittest.TestCase):
    def test_fixed_generations_and_parent_child_relation(self):
        raw=payload()
        self.assertIn('actor(5463,1373880,',raw)
        self.assertIn('actor(5489,1373951,',raw)
        self.assertIn("'/usr/bin/python3.14',set(),5463)",raw)
        self.assertIn("assert len(old_names)==1 and int(daemon.GetConnectionUnixUser(old_names[0]))==0",raw)

    def test_no_live_signal_or_server_lifecycle_operation(self):
        raw=payload();tree=ast.parse(raw)
        forbidden={'kill','pidfd_send_signal','system','StartUnit','StopUnit','RestartUnit','Reload','KillUnit'}
        self.assertFalse(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in forbidden for n in ast.walk(tree)))
        self.assertNotIn('pg_terminate_backend',raw)
        self.assertIn("phase='WHOLE_TWO_READ';before=read();assert before==read()",raw)
        self.assertIn('except BaseException as failure:retained_error(failure)',raw)

    def test_independent_fixed_server_binding_predicates(self):
        raw=payload()
        for expected in ("v['role']=='schubert_batch'", "v['application']=='PG243-cold-empty'",
                         "v['database']=='schubert_nk'", "v['state']in ('active','idle in transaction')",
                         "assert v['query']==heartbeat", 'assert len(tcp)==1',
                         "v['backendStart']and v['transactionStart']"):
            self.assertIn(expected,raw)
        self.assertIn('all(snapshot[k]==sealed[k]',raw)
        self.assertIn('first==tree_identity()and server==peer()',raw)


if __name__=='__main__':
    unittest.main()
