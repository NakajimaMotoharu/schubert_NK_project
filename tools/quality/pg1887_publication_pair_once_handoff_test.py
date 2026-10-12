"""Actual generated current31/90 full-parent and owned child-pipe guards."""
import ast
import copy
import stat
import unittest
from pg1887_publication_pair_once_handoff import payload


def fixture():
    fds={str(i):{'metadata':[1,i+1,0,0,stat.S_IFREG|0o400,1,1,10,10],'target':'fixed-file-'+str(i)}for i in range(101)}
    for n in ['31','90']:fds[n]={'metadata':[2,123,0,0,stat.S_IFDIR|0o755,2,4096,10,10],'target':'/run'}
    fds['99']['target']='pipe:[101]';fds['100']['target']='pipe:[102]'
    return {'pid':490998,'ticks':9782388,'argvSha256':'a'*64,'authority':{'Uid':'0 0 0 0'},'cgroup':'0::/fixed','fds':fds}


class Current(unittest.TestCase):
    def test_actual_full_parent_and_only_two_child_pipes(self):
        tree=ast.parse(payload());names={'fresh_parent','parent_after_ref'};nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names];self.assertEqual(2,len(nodes));ns={}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual parent history guards>','exec'),ns)
        old=fixture();self.assertTrue(ns['fresh_parent'](old,copy.deepcopy(old),20))
        for fd in ['31','90']:
            bad=copy.deepcopy(old);bad['fds'][fd]['metadata'][1]+=1
            with self.assertRaises(ValueError):ns['fresh_parent'](old,bad,20)
        gone=copy.deepcopy(old);del gone['fds']['99'];del gone['fds']['100']
        self.assertTrue(ns['parent_after_ref'](old,gone,{'pipe:[101]','pipe:[102]'}))
        for mutate in ['foreign','pid','extra']:
            bad=copy.deepcopy(gone)
            if mutate=='foreign':bad['fds']['30']['target']='foreign'
            elif mutate=='pid':bad['pid']+=1
            else:del bad['fds']['30']
            with self.assertRaises(ValueError):ns['parent_after_ref'](old,bad,{'pipe:[101]','pipe:[102]'})

    def test_actual_source_same_connection_reserve_before_send(self):
        r=payload()
        self.assertIn("'currentPublicationNotStarted'",r)
        self.assertIn("children == (set()if REF_CLOSED else{491029})",r)
        self.assertIn("fresh['parent']['fds']['31']",r);self.assertIn("fresh['parent']['fds']['90']",r)
        self.assertIn('terminate(491029, 9782567',r);self.assertIn('terminate(490998, 9782388',r)
        self.assertLess(r.index("private('fresh-complete.private'"),r.index('terminate(491029'))
        forbidden=[n for n in ast.walk(ast.parse(r))if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='signal'and n.attr=='SIGKILL']
        self.assertEqual([],forbidden)


if __name__=='__main__':unittest.main()
