import ast
import unittest
from pathlib import Path
import hashlib
import pg2208_current_newboot_cold_sources as p


class NewBootCold(unittest.TestCase):
    def test_independent_current_tuple_and_no_authority(self):
        j=p.java();r=p.observer()
        for value in ['b2d6f605-61cf-425f-8fbd-12d606f6ee66','3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8',
          '62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c','PG2126',
          '02bddddf-9cd3-4668-9d67-7561232fc4e4','20b86040-ffd5-4d17-9fca-5d83048ba905',
          '2026-10-13T06:29:34.698736Z','2026-10-13T06:56:23.969590Z']:
            self.assertIn(value,j)
        self.assertIn('done.outcome()==MaintenanceCompletion.Outcome.WARNING',j)
        for value in ['PG1292','pg1441-current-cold','d2e3a86f','841b507c','systemctl start','invalidate(','.revoke(','issuePermit']:
            self.assertNotIn(value,j+r)
        self.assertIn('refs.check("prepared");original(session);',j)
        self.assertIn('PEER_CLOSED=True',r);self.assertIn('PREPARED=True',r)
        self.assertIn('metadata(ROOT/name)==before_runtime[name]',r)
        self.assertIn("require(boot==BOOT)",r)

    def test_whole_role_matrix_and_current_signature(self):
        r=p.observer();tree=ast.parse(r)
        a=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ROLE_IDS' for t in n.targets))
        self.assertEqual(ast.literal_eval(a.value),{'backup':(992,977),'cleanup':(0,0),'expiry':(0,0),'inspector':(991,976),
          'ordinary-api193':(999,981),'ordinary-bootstrap196':(999,981),'ordinary-inspector196':(991,976),
          'ordinary-web193':(997,980),'parent':(0,0),'root-api':(0,0),'root-api193':(0,0),'root-web193':(0,0)})
        h=hashlib.sha256(Path('/home/mini/codex/project1/work/pgpt-vm/private/pg2126-manifest-v1.sig').read_bytes()).hexdigest()
        self.assertEqual(h,'7ef03cf927c2f5b79b39a5d5187db439c753c57933bfff18b26386a02afaf449')
        self.assertIn(h,r)
        self.assertIn("snapshot=observe",r)
        self.assertIn("peer_check()",r)
        self.assertIn("rows==old['rows'] and len(rows)==24",r)


if __name__=='__main__':unittest.main()
