"""Independent extraction of actual command, not just the declared test/module mapping."""
import ast
import unittest
from pyflakes.api import check,checkPath
import pg4674_root_identity_complete_selection as selection


class CompleteSelection(unittest.TestCase):
    def test_actual_command_module_set_and_no_suppression(self):
        raw=selection.source();nodes=ast.walk(ast.parse(raw))
        commands=[n.value for n in nodes if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='command'for t in n.targets)]
        self.assertEqual(1,len(commands));args=commands[0].elts
        index=next(i for i,n in enumerate(args)if isinstance(n,ast.Constant)and n.value=='-pl')
        projects=args[index+1].value
        self.assertEqual({'protocol','storage','bootstrap','api','web','batch'},{p.removeprefix('src/schubert-nk-')for p in projects.split(',')})
        self.assertEqual(set(selection.previous.MODULES.values()),{p.removeprefix('src/schubert-nk-')for p in projects.split(',')})
        self.assertNotIn('failIfNoTests=false',raw);self.assertIn('if actual != expected',raw)
        ns='\n'.join(n+'=None'for n in ['os','SOURCE','ROOT','WORK','tarfile','TESTS','MODULES','re','TOOLCHAIN','subprocess','datetime','Path','hashlib','ET','json','sha'])+'\n'
        self.assertEqual(0,check(ns+raw,'<actual all-six selected command>'))
        self.assertEqual(0,checkPath(selection.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
