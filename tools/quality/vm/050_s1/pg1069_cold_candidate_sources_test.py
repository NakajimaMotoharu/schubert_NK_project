"""PT-DEP-1069001..004: independent source/authority/delta rejection oracles."""
import ast
import unittest
from pg1069_cold_candidate_sources import files,replace_once,stage_body


class ColdCandidate(unittest.TestCase):
    def test_new_slots_and_no_runtime_preparation_replay(self):
        value=files()
        self.assertEqual({'Pg1069ColdCandidateStage.java','Pg1069ColdCandidateStageTest.java','pg1069_cold_refs.py'},set(value))
        java=value['Pg1069ColdCandidateStage.java']
        self.assertIn('args!=null',java)
        self.assertIn('"place".equals(args[0])',java)
        self.assertNotIn('static void environment()',java)
        self.assertNotIn('freezeCandidate()',java)
        self.assertIn('database.setReadOnly(true)',java)
        self.assertIn('pg_try_advisory_lock(71419602)',java)
        self.assertIn('original(session)',java)
        for source in value.values():
            self.assertNotIn('pg1062-cold-prepared-v1',source)
            self.assertNotIn('pg1062-cold-tools-v1',source)

    def test_qualified_stage_before_anchored_after_and_exact_prepared_fds(self):
        py=files()['pg1069_cold_refs.py'];ast.parse(py)
        self.assertIn('PREPARED=True',py)
        self.assertNotIn('fixed[5]+5',py)
        self.assertIn('  require(m==fixed)',py)
        self.assertLess(py.index("phase='SIGNED_UNUSED_STAGE'"),py.index('\n authenticate()'))
        self.assertLess(py.index('tar.extractall(root'),py.index('\n authenticate()'))
        self.assertIn('require(after==before and runtime==runtime_namespaces())',py)
        self.assertIn('while True:time.sleep(1)',py)

    def test_archive_signature_full_payload_and_mutation_limits(self):
        body=stage_body();ast.parse(body)
        self.assertIn("data['source']['commit']==SOURCE",body)
        self.assertIn("data['release']=='0.1.0-PG1068'",body)
        self.assertIn("len(data['artifacts'])==187",body)
        self.assertIn("policy['check_members']",body)
        self.assertLess(body.index("tar.extractfile(row['path'])"),body.index('root.mkdir('))
        self.assertIn("sig.open('xb')",body)
        self.assertIn("'openssl','pkeyutl','-verify'",body)
        self.assertNotIn('current.readlink()',body)
        for forbidden in ('unlink(', 'systemctl','invalidate(', 'migrate', 'chmod(0o777'):
            self.assertNotIn(forbidden,body)

    def test_missing_duplicate_null_source_markers_refuse(self):
        self.assertEqual('aZb',replace_once('axb','x','Z'))
        for text in ('ab','xx'):
            with self.assertRaises(ValueError):replace_once(text,'x','Z')
        for args in ((None,'x','Z'),('x',None,'Z'),('x','x',None),('x','','Z')):
            with self.assertRaises(ValueError):replace_once(*args)

    def test_candidate_local_source_cannot_replace_current_scope(self):
        tree=ast.parse(stage_body())
        self.assertEqual(2,len(tree.body))
        fn,call=tree.body
        self.assertIsInstance(fn,ast.FunctionDef)
        self.assertEqual('place_candidate',fn.name)
        self.assertIsInstance(call,ast.Expr)
        self.assertEqual('place_candidate',call.value.func.id)
        self.assertFalse(any(isinstance(n,(ast.Global,ast.Nonlocal))for n in ast.walk(fn)))
        source=[n for n in fn.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SOURCE'for t in n.targets)]
        self.assertEqual(1,len(source))
        # Execute only assignments, no IO/VM/archive operations, in an independent
        # minimal function. Literal current and candidate identities are separate.
        mini=ast.FunctionDef(name='candidate_local',args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),
             body=source+[ast.Return(ast.Name(id='SOURCE',ctx=ast.Load()))],decorator_list=[])
        env={'SOURCE':'40ef6e894573d2ffab1d1732124960f9c98d5f97'}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[mini],type_ignores=[])),'independent local source fixture','exec'),env)
        self.assertEqual('d5b00104280028d9ea81b44c1d1c805f3c2861ed',env['candidate_local']())
        self.assertEqual('40ef6e894573d2ffab1d1732124960f9c98d5f97',env['SOURCE'])


if __name__=='__main__':unittest.main()
