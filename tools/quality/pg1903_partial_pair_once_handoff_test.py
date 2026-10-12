"""Actual102FD generated guards and exact current pair; no repeat publication/reload."""
import ast
import copy
import unittest
from pg1887_publication_pair_once_handoff_test import fixture
from pg1903_partial_pair_once_handoff import payload


class Partial(unittest.TestCase):
    def test_actual_102_parent_and_only_child_pipes(self):
        r=payload();tree=ast.parse(r);names={'fresh_parent','parent_after_ref'};nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names];ns={}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual102 history>','exec'),ns)
        old=fixture();old['pid']=493115;old['ticks']=9883172;old['fds']['129']=copy.deepcopy(old['fds']['31']);old['fds']['129']['target']='/run/schubert-nk/startup'
        self.assertEqual(102,len(old['fds']))
        self.assertTrue(ns['fresh_parent'](old,copy.deepcopy(old),20))
        gone=copy.deepcopy(old);del gone['fds']['99'];del gone['fds']['100']
        self.assertTrue(ns['parent_after_ref'](old,gone,{'pipe:[101]','pipe:[102]'}))
        bad=copy.deepcopy(gone);del bad['fds']['129']
        with self.assertRaises(ValueError):ns['parent_after_ref'](old,bad,{'pipe:[101]','pipe:[102]'})
        self.assertIn('terminate(493146, 9883367',r);self.assertIn('terminate(493115, 9883172',r)
        self.assertIn("'partialPublicationQualified'",r);self.assertIn("'reloadNotReserved'",r)
        self.assertNotIn("subprocess.run(['/usr/bin/systemctl', 'daemon-reload']",r)


if __name__=='__main__':unittest.main()
