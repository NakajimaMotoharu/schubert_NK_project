"""Independent newboot/current tuple, complete role/ownership and zero business authority guards."""
import ast
import unittest
from pyflakes.api import check
import pg2816_network_current_cold_sources as p


class CurrentColdSources(unittest.TestCase):
    def test_exact_current_tuple_and_no_original_run_replay(self):
        j=p.java();r=p.observer();self.assertEqual(0,check(r,'<whole actual finite Ref graph>'))
        for value in [p.BOOT,p.SOURCE,p.BOM,p.CLASS,'PG2654','77601cf8-0ade-40fd-813f-c81d5210845e',
            '26250063-8755-43b6-9ac7-f76d5eee7257','2026-10-14T06:56:07.778154Z','2026-10-14T07:24:35.698243Z']:
            self.assertTrue(value in j,value)
        self.assertFalse('b2d6f605'in j,'old boot cannot be Java current owner')
        self.assertTrue("boot!='b2d6f605"in r,'old boot explicitly rejected, not deleted from refusal oracle')
        for value in ['02bddddf','PG2126','systemctl start','invalidate(','.revoke(','issuePermit']:
            self.assertFalse(value in j+r,value)
        for value in ["'unitFiles':unit_vectors(saved['unitFilesActual'])",'locks.owned_flocks(',
            'PEER_CLOSED=True','PREPARED=True','metadata(ROOT/name)==before_runtime[name]',"snapshot=observe",p.SIG]:self.assertIn(value,r)
        self.assertNotIn("require(peers.splitlines()==[b'0',b'0'])",r)
        self.assertNotIn("int(d[2]))!=(os.major(m[0])",r)
        self.assertIn('refs.check("prepared");original(session);',j)
        self.assertIn('done.outcome()==MaintenanceCompletion.Outcome.WARNING',j)

    def test_all_twelve_role_ids_fixed_and_no_missing_owned_lock_checks(self):
        tree=ast.parse(p.observer())
        node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ROLE_IDS'for t in n.targets))
        self.assertEqual({'backup':(992,977),'cleanup':(0,0),'expiry':(0,0),'inspector':(991,976),
            'ordinary-api193':(999,981),'ordinary-bootstrap196':(999,981),'ordinary-inspector196':(991,976),
            'ordinary-web193':(997,980),'parent':(0,0),'root-api':(0,0),'root-api193':(0,0),'root-web193':(0,0)},ast.literal_eval(node.value))
        self.assertIn('actor()==fixed_parent',p.observer())


if __name__=='__main__':unittest.main()
