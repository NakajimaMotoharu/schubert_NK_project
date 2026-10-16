import ast
import inspect
import pathlib
import tempfile
import types
import unittest
import pg4830_new_current_bootstrap_catalog as catalog
import pg4832_new_current_bootstrap_native as native


class CurrentNative(unittest.TestCase):
    def test_complete_binding_and_two_point_counts(self):
        raw=catalog.payload();ast.parse(raw)
        self.assertIn('len(points)==12',raw)
        self.assertIn('metadata9(p.lstat())==metadata9(s)',raw)
        server=native.server();source=native.source();ast.parse(server);ast.parse(source)
        self.assertIn("len(v['selected'])==12",server)
        self.assertIn("'currentNativeStreams':10,'validatedNativePoints':12",server)
        self.assertIn("catalog['selected'])!=12",source)
        self.assertIn(catalog.SLOT+'/manifest.safe.json',source)
        self.assertIn(".read_bytes())['result']",source)
        self.assertNotIn('PG4782-native',source);self.assertNotIn('PG4782-native',server)
        self.assertIn('3739',server)
        self.assertIn("'mainClasses':1646",inspect.getsource(native.previous.qualify))
        self.assertIn("qualified['jarHashes'][m]",server)

    def pair(self,change=None):
        with tempfile.TemporaryDirectory()as root:
            calls=[]
            points=[{'unit':'other','relative':str(i)}for i in range(10)]+[
                {'unit':'schubert-nk-bootstrap-admin.service','relative':'new.closing.exec'},
                {'unit':'schubert-nk-bootstrap-admin.service','relative':'new.terminal.exec'}]
            sessions=[{}for _ in range(10)]+[
                {'sessionIdSha256':'same','startMs':100,'dumpMs':120},
                {'sessionIdSha256':'same','startMs':100,'dumpMs':110}]
            if change:change(points,sessions)
            def require(v):
                if not v:raise ValueError('fixture refusal')
            def run(args,**kwargs):
                calls.append(args);return types.SimpleNamespace(returncode=0,stderr=b'',stdout=b'sameSessionProbeMonotonic=true;latestClosingOnly=true\n')
            ns={'v':{'selected':points},'sessions':sessions,'require':require,'J':pathlib.Path('/fixture'),'cp':'fixture','streams':[pathlib.Path(str(i))for i in range(12)],'early_index':1,'subprocess':types.SimpleNamespace(run=run),'O':pathlib.Path(root)}
            exec(compile(native.PAIR,'<literal bootstrap pair>','exec'),ns)
            self.assertEqual([str(p)for p in ns['streams']],['0','2','3','4','5','6','7','8','9','10'])
            self.assertEqual(calls[0][-2:],['11','10'])

    def test_pair_and_dominance_negative_vectors(self):
        self.pair()
        for field,value in [('sessionIdSha256','foreign'),('startMs',101),('dumpMs',121)]:
            def mutation(points,sessions,f=field,v=value):sessions[11][f]=v
            with self.assertRaises(ValueError):self.pair(mutation)
        with self.assertRaises(ValueError):self.pair(lambda p,s:p[11].update(relative='not-a-terminal'))


if __name__=='__main__':unittest.main()
