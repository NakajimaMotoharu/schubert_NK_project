"""Independent fixed permissions, canonical sidecar and Ref lifetime scope."""
import ast
import copy
import io
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
import pg4520_failed_current_unused_post as p


class UnusedPost(unittest.TestCase):
    def test_independent_root_schubert_permission_matrix_and_all_mutations(self):
        records=[{'path':name,'directory':directory,'uid':0,'gid':986,'mode':mode,'nlink':links,'symlink':False,'xattrs':[]}for name,directory,mode,links in
          [('.',True,0o750,3),('operations',True,0o750,2),('operations/bin/schubert-nkctl',False,0o750,1),('operations/bin/schubert-nk-inbox-inspector',False,0o750,1),('VERSION',False,0o640,1)]]
        self.assertTrue(p.permissions(records))
        for i in range(len(records)):
            for field in records[i]:
                if field=='path':continue  # inventory/path oracle is the pinned signed187 loop, not the permission matrix
                bad=copy.deepcopy(records);bad[i][field]=None
                with self.subTest(i=i,field=field),self.assertRaises(ValueError):p.permissions(bad)
        for field,value in [('uid',1),('gid',0),('mode',0o644),('nlink',2),('symlink',True),('xattrs',['foreign'])]:
            bad=copy.deepcopy(records);bad[-1][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):p.permissions(bad)

    def test_actual_candidate_canonical_sidecar_has_literal_newline_order(self):
        raw=p.candidate_check();tree=ast.parse(raw)
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='candidate_verify')
        assignment=next(n for n in ast.walk(fn)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='canonical'for t in n.targets))
        ns={'sums':{'b':'2'*64,'a':'1'*64}}
        exec(compile(ast.Module(body=[assignment],type_ignores=[]),'<actual canonical sidecar>','exec'),ns)
        self.assertEqual(('1'*64+'  a\n'+'2'*64+'  b\n').encode('ascii'),ns['canonical'])

    def test_actual_both_candidate_reads_are_inside_ten_ref_scope_before_normal_close(self):
        raw=p.payload();self.assertEqual(0,check(raw,'<whole unused candidate post>',Reporter(io.StringIO(),io.StringIO())))
        tree=ast.parse(raw);scope=next(n for n in tree.body if isinstance(n,ast.Try)and n.finalbody)
        calls=[n for n in ast.walk(scope)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='candidate_verify']
        self.assertEqual(2,len(calls));self.assertTrue(all(n.lineno<scope.finalbody[0].lineno for n in calls))
        self.assertIn('require(candidate_first==candidate_second)',raw)
        self.assertNotIn('PG3748',p.candidate_check());self.assertNotIn('candidateAbsent',raw)


if __name__=='__main__':unittest.main()
