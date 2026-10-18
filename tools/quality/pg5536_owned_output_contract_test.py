"""No VM action: output collisions before constructor/SSH, frozen graph unchanged."""
import ast
import builtins
import inspect
import symtable
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg5532_current_owned_stop_retry as entry
import pg5534_current_owned_post_retry as post
import pg2556_strict_current_owned_dispatch as constructor_source


class Outputs(unittest.TestCase):
    def test_each_auxiliary_collision_and_symlink_rejected_before_constructor(self):
        with tempfile.TemporaryDirectory()as name:
            root=Path(name);entry.ensure_outputs(root)
            for target in entry.output_paths(root):
                with self.subTest(path=target.name):
                    target.touch()
                    with patch.object(entry,'W',root),patch.object(entry.previous,'namespace')as constructor,self.assertRaises(ValueError):entry.action()
                    constructor.assert_not_called();target.unlink()
            target=entry.output_paths(root)[0];target.symlink_to(root/'missing')
            with self.assertRaises(ValueError):entry.ensure_outputs(root)

    def test_all_writers_are_new_no_old_run_and_stage_remains_actual(self):
        raw=entry.run_source()
        constructor=entry.previous.namespace()['run_action']
        source=entry.previous.role.bind(inspect.getsource(constructor_source.run_action));env={**constructor.__globals__}
        exec(compile(source,'<actual deferred original constructor>','exec'),env)
        self.assertEqual(constructor.__code__.co_code,env['run_action'].__code__.co_code)
        self.assertEqual(constructor.__code__.co_consts,env['run_action'].__code__.co_consts)
        tree=ast.parse(source);fn=tree.body[0];self.assertEqual(len(fn.body),4)
        fn.body=fn.body[:2]+[ast.Return(value=ast.Name(id='ns',ctx=ast.Load()))]
        exec(compile(ast.fix_missing_locations(tree),'<constructor namespace only, no operation>','exec'),env)
        runtime=env['run_action']('NO_OPERATION');exec(compile(raw,'<new output contract only>','exec'),runtime)
        symbols=symtable.symtable(raw,'<exact stop references>','exec')
        refs={s.get_name()for child in symbols.get_children()for s in child.get_symbols()if s.is_global()and s.is_referenced()}
        self.assertEqual([],sorted(name for name in refs if name not in runtime and not hasattr(builtins,name)))
        defined={node.name for node in ast.parse(raw).body if isinstance(node,(ast.FunctionDef,ast.ClassDef))}
        header='\n'.join(name+'=None'for name in sorted(runtime)if name.isidentifier()and name not in defined)+'\n'
        self.assertEqual(check(header+raw,'<corrected entire original stop and actual namespace>'),0)
        for marker in(entry.PARENT,entry.PRESTOP,"('pg5532-' + action + '-v1')","'pg5500-stage-v1.exit'","'pg5498-frozen-v1.safe.json'"):
            self.assertIn(marker,raw)
        self.assertNotIn('pg5063',raw);self.assertNotIn('.write_bytes(r.stderr)',raw)
        self.assertEqual(raw.count(".open('xb') as preserved_error:"),2)
        self.assertIn('capture_output=True, timeout=300',raw);self.assertIn('capture_output=True, timeout=30',raw)
        tree=ast.parse(raw);f=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='run_action')
        calls=[n for n in ast.walk(f)if isinstance(n,ast.Call)]
        self.assertFalse(any(isinstance(n.func,ast.Attribute)and n.func.attr=='write_bytes'for n in calls))

    def test_post_only_receipt_and_output_changed_no_fabricated_success(self):
        original=post.previous.namespace()['entry']();fixed=post.namespace()['entry']()
        self.assertEqual(original.__code__.co_code,fixed.__code__.co_code)
        self.assertIn('pg5532-stop-v1.safe.json',fixed.__code__.co_consts);self.assertNotIn('pg5500-stop-v1.safe.json',fixed.__code__.co_consts)
        self.assertEqual(fixed.__globals__['SLOT'],post.SLOT)
        emitted=post.namespace()['emit'];closed=inspect.getclosurevars(emitted)
        self.assertEqual(closed.nonlocals['emit_fn'].__globals__['SLOT'],post.SLOT)
        with patch.object(fixed.__globals__['subprocess'],'check_output',return_value=b''),patch.object(Path,'read_bytes',return_value=b'{"actualExit":1,"sourceQualified":false}'),patch.object(fixed.__globals__['subprocess'],'run')as run,self.assertRaises(ValueError):fixed()
        run.assert_not_called()
        for item in(entry,post):self.assertEqual(checkPath(item.__file__),0)
        self.assertEqual(checkPath(__file__),0)


if __name__=='__main__':unittest.main()
