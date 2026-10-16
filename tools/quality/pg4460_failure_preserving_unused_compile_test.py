"""Execute actual host command-loop/gate AST with independent exit sequences."""
import ast
import datetime
import hashlib
from pathlib import Path
import tempfile
import types
import unittest
import pg4460_failure_preserving_unused_compile as subject


class PreserveFirstPhase(unittest.TestCase):
    def test_actual_phase_loop_never_qualifies_failed_or_unrun_commands(self):
        tree = ast.parse(subject.compiler()); main = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == 'main')
        start = next(i for i,n in enumerate(main.body) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple)
                     and [getattr(v,'id',None) for v in n.target.elts] == ['label','argv'])
        gate = next(i for i,n in enumerate(main.body) if isinstance(n,ast.If) and ast.unparse(n.test) == 'r.returncode == 0')
        statements = main.body[start:gate+1]
        value = next(n for n in main.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id == 'value' for t in n.targets))
        selected = [(k,v) for k,v in zip(value.value.keys,value.value.values) if isinstance(k,ast.Constant) and k.value in ['actualExit','completeGraphQualified','phases']]
        statements += [ast.Assign(targets=[ast.Name(id='observed',ctx=ast.Store())],value=ast.Dict(keys=[k for k,_ in selected],values=[v for _,v in selected]))]
        code = compile(ast.fix_missing_locations(ast.Module(body=statements,type_ignores=[])), '<actual failure preserving loop/gate>', 'exec')
        for exits, expected_calls, expected_status, gate_calls in [([1],1,1,0),([0,1],2,1,0),([0,0,0],3,0,1)]:
            with tempfile.TemporaryDirectory() as folder:
                calls = []; validated = []
                def run(argv,stdout,stderr):
                    status = exits[len(calls)];calls.append(argv);stdout.write(b'independent literal output\n')
                    return types.SimpleNamespace(returncode=status)
                namespace = {'commands':[('compile',['fixed-javac']),('fixture1',['fixed-java','one']),('fixture2',['fixed-java','two'])],
                    'W':Path(folder),'TARGET':Path(folder),'phases':{},'subprocess':types.SimpleNamespace(run=run),'os':__import__('os'),
                    'inventory':lambda target:{},'validate_actual_graph':lambda target,hashes:validated.append((target,hashes)),
                    'sha':lambda path:hashlib.sha256(path.read_bytes()).hexdigest(),'datetime':datetime}
                exec(code,namespace)
                self.assertEqual(expected_calls,len(calls));self.assertEqual(gate_calls,len(validated))
                self.assertEqual(expected_status,namespace['observed']['actualExit'])
                self.assertIs(expected_status==0,namespace['observed']['completeGraphQualified'])
                self.assertEqual(expected_calls,len(namespace['observed']['phases']))
                self.assertTrue(all(len(v['logSha256'])==64 for v in namespace['observed']['phases'].values()))
        raw = subject.compiler()
        self.assertIn("write(W / 'pg4460-frozen-v1.safe.json'",raw)


if __name__ == '__main__':
    unittest.main()
