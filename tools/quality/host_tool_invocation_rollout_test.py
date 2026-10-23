"""Static call-order contract of every changed library; no actual jobs are executed."""
import ast
import unittest
from pathlib import Path

FOLDER=Path(__file__).resolve().parent
LIBRARIES=('pg6990_recovery_public_scan.py','pg7006_monitoring_pure_host.py',
 'pg7008_monitoring_mode_post.py','pg7030_monitoring_six_compile.py',
 'pg7032_monitoring_six_artifact_post.py','pg7036_c02_four_template_host.py')


def validate(tree):
    main=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='main')
    first=main.body[0]
    if not (isinstance(first,ast.Assign) and isinstance(first.targets[0],ast.Name)
      and first.targets[0].id=='invocation' and isinstance(first.value,ast.Call)
      and isinstance(first.value.func,ast.Name) and first.value.func.id=='capture'):
        raise ValueError('capture precedes all job/publication side effects')
    checks=[i for i,node in enumerate(main.body) if isinstance(node,ast.Expr)
      and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name)
      and node.value.func.id=='verify' and ast.dump(node.value.args[0])==ast.dump(ast.Name(id='invocation',ctx=ast.Load()))]
    if len(checks)!=1:raise ValueError('one same-record terminal verification required')
    serializations=[i for i,node in enumerate(main.body) for call in ast.walk(node)
      if isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute)
      and call.func.attr in ('write','mkdir','open')]
    if not any(i>checks[0] for i in serializations):
        raise ValueError('verification precedes final publication')
    if not any(isinstance(node,ast.keyword) and node.arg=='invocation'
       and isinstance(node.value,ast.Name) and node.value.id=='invocation' for node in ast.walk(main)):
        raise ValueError('actual invocation is serialized separately from child command')
    return True


class RolloutContractTest(unittest.TestCase):
    def test_all_six_libraries_capture_bind_verify_before_publish(self):
        for name in LIBRARIES:
            with self.subTest(library=name):self.assertTrue(validate(ast.parse((FOLDER/name).read_text())))

    def test_missing_terminal_verification_is_detected(self):
        tree=ast.parse((FOLDER/'pg7006_monitoring_pure_host.py').read_text())
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        main.body=[n for n in main.body if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
                   and isinstance(n.value.func,ast.Name) and n.value.func.id=='verify')]
        with self.assertRaises(ValueError):validate(tree)

    def test_missing_capture_and_binding_are_detected(self):
        for change in ('capture','binding'):
            tree=ast.parse((FOLDER/'pg7008_monitoring_mode_post.py').read_text())
            main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
            if change=='capture':main.body.pop(0)
            else:
                for node in ast.walk(main):
                    if isinstance(node,ast.keyword) and node.arg=='invocation':node.arg='not_invocation'
            with self.assertRaises(ValueError):validate(tree)


if __name__=='__main__':
    unittest.main()
