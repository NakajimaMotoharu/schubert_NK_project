"""Independent literal tuples/delta/argument guards; not Production acceptance."""
import ast
import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg2832_network_cold_unused_sources as p


class ColdUnused(unittest.TestCase):
    def test_current_candidate_are_local_distinct_and_exact(self):
        raw=p.observer('1'*64);self.assertEqual(0,check(raw,'<whole unused graph>'))
        j=p.java()
        for v in ['79a3260a-e16d-42bf-942a-b914ed144c28','04207efc3ad78bca75942153a90c70985064c988',
            '552c5e25591483ee2c9aa95c6b8170f37e3390b14bd08ed88bfc0c4870002a37','PG2654',p.CLASS]:
            self.assertTrue(v in j,v)
        self.assertTrue('"place".equals(args[0])'in j)
        self.assertFalse('static void environment()'in j)
        self.assertFalse('freezeCandidate()'in j)
        self.assertTrue("[b'"+p.CLASS+"',b'place',b'']"in raw)
        tree=ast.parse(p.stage_body());fn=tree.body[0]
        self.assertIsInstance(fn,ast.FunctionDef)
        self.assertFalse(any(isinstance(n,(ast.Global,ast.Nonlocal))for n in ast.walk(fn)))
        assigns={n.targets[0].id:ast.literal_eval(n.value)for n in fn.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in {'SOURCE','DIGEST'}}
        self.assertEqual({'SOURCE':'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25','DIGEST':'37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863'},assigns)

    def test_bounded_mutation_before_ancestry_and_no_authority(self):
        r=p.observer('1'*64);j=p.java()
        self.assertLess(r.index("phase='SIGNED_UNUSED_STAGE'"),r.index('   authenticate();before_inventory='))
        for v in ['runtime==before[\'runtime\']','actor()==fixed_parent','locks.owned_flocks(',"'ordinary-web193':(997,980)",p.PREPARE_SHA]:self.assertTrue(v in r,v)
        body=p.stage_body()
        self.assertLess(body.index("tar.extractfile(row['path'])"),body.index('root.mkdir('))
        for v in ['systemctl start','issuePermit','invalidate(','.revoke(','os.replace(','unlink(']:self.assertFalse(v in j+body,v)
        self.assertTrue('database.setReadOnly(true)'in j)
        self.assertTrue('while True:time.sleep(1)'in r)
        self.assertTrue('PEER_CLOSED=True'in r)

    def test_missing_duplicate_boundary_and_post_failure_refuse(self):
        for value in [None,'','z'*64,'a'*63]:
            with self.assertRaises(ValueError):p.observer(value)
        for value in ['', 'xx']:
            with self.assertRaises(ValueError):p.one(value,'x','y')
        with patch.object(p.current.W.__class__,'read_bytes',return_value=b'{"actualExit":0,"guest":{"actualExit":1}}'):
            with self.assertRaises(ValueError):p.qualify()


if __name__=='__main__':unittest.main()
