"""Independent missing/suffix/import/hash/name vectors and actual source joins."""
import copy
import unittest
from pyflakes.api import check
from pg1681_input_closure_contract import validate_graph,canonical
from pg1681_closed_candidate_sources import sources
import pg1682_closed_candidate_compile as compiler
import pg1683_closed_unused_dispatch as dispatch


def vector():
    pins={n:'a'*64 for n in ['pg1681_input_preflight.py','pg1640_native_refs.py','pg_child.py','Pg1640UnusedStage.class','Pg1640UnusedStage$References.class']}
    text={'pg1681_input_preflight.py':'import os\n','pg1640_native_refs.py':"from pg_child import f\narchive='pg1683-release-v4.tar'\n",'pg_child.py':'import json\n'}
    return pins,text,{'pg1683-release-v4.tar','pg1638-manifest-v1.sig','bundle.safe.json'}


class ClosedInputTest(unittest.TestCase):
    def test_independent_valid_and_missing_foreign_suffix_vectors(self):
        p,s,n=vector();self.assertTrue(validate_graph(p,s,'pg1683-release-v4.tar',n))
        for kind in ['archiveOld','extra','missing','depMissing','sourceMissing','foreign','relative','badSha','boolSha','pathEscape','classMissing','childOld']:
            p,s,n=vector();name='pg1683-release-v4.tar'
            if kind=='archiveOld':name='pg1683-release-v1.tar'
            elif kind=='extra':n.add('foreign.tar')
            elif kind=='missing':n.remove('bundle.safe.json')
            elif kind=='depMissing':del p['pg_child.py'];del s['pg_child.py']
            elif kind=='sourceMissing':del s['pg_child.py']
            elif kind=='foreign':s['pg_child.py']='import foreign\n'
            elif kind=='relative':s['pg_child.py']='from . import foreign\n'
            elif kind=='badSha':p['pg_child.py']='x'*64
            elif kind=='boolSha':p['pg_child.py']=True
            elif kind=='pathEscape':p['../foreign.py']='a'*64
            elif kind=='classMissing':del p['Pg1640UnusedStage$References.class']
            elif kind=='childOld':s['pg1640_native_refs.py']=s['pg1640_native_refs.py'].replace('release-v4','release-v1')
            with self.assertRaises(ValueError,msg=kind):validate_graph(p,s,name,n)
        for bad in [None,True,{},[]]:
            p,s,n=vector()
            with self.assertRaises(ValueError):validate_graph(bad,s,'pg1683-release-v4.tar',n)
        for bad in ['',None,True,'a//b','a/../b','/a','a\\b']:
            with self.assertRaises(ValueError):canonical(bad)

    def test_actual_compiler_child_and_transfer_join_before_ownership(self):
        generated=sources('a'*64);refs=generated['pg1640_native_refs.py'];pre=generated['pg1681_input_preflight.py'];java=generated['Pg1640UnusedStage.java']
        for raw in [refs,pre]:
            self.assertIn('pg1683-release-v4.tar',raw)
        self.assertNotIn('pg1661-release-v1.tar',refs)
        self.assertLess(java.index('beforeOwnership(Pg1640UnusedStage::verifyInputClosure);'),java.index('require(MaintenanceFileLock.create()'))
        for name,raw in generated.items():
            if name.endswith('.py'):
                if name in ['pg1640_native_refs.py','pg1681_input_preflight.py']:raw="BUNDLE_HASH='"+'a'*64+"'\n"+raw
                self.assertEqual(0,check(raw,'<generated '+name+'>'))
        self.assertIn('validate_graph(hashes,',compiler.compiler())
        self.assertIn('Pg1681InputBoundaryTest.java',compiler.compiler())
        self.assertIn('pg1683-release-v4.tar',dispatch.source())
        self.assertIn("'Pg1681InputBoundaryTest','Pg1640UnusedStage place'",dispatch.source())
        ns=dispatch.namespace({'actualExit':0,'candidateSource':'2741c4546afad6c1e8b6efbd53dfb58144edf7bb','manifestSha256':'a'*64})
        self.assertEqual('/home/ubuntu/pg1683-candidate-input-v4',ns['REMOTE'])
        self.assertEqual('/var/lib/pgpt-s1-preservation/pg1681-completed-unused-tools-v4',ns['GUEST'])

    def test_generated_all_import_closure_and_stability(self):
        g=sources('a'*64);p,s,n=vector()
        p.update({name:'a'*64 for name in g if name.endswith('.py')});s={name:raw for name,raw in g.items()if name.endswith('.py')}
        del p['pg_child.py']
        self.assertTrue(validate_graph(p,s,'pg1683-release-v4.tar',n))
        self.assertEqual(copy.deepcopy(g),sources('a'*64))


if __name__=='__main__':unittest.main()
