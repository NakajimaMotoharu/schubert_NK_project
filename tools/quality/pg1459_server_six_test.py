import unittest
import ast
from pathlib import Path
from pg1459_server_six import complete_result


class FullGateTest(unittest.TestCase):
    def test_explicit_child_umask_and_no_implicit_jvm_banner(self):
        tree=ast.parse(Path(__file__).with_name('pg1459_server_six.py').read_text())
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)]
        run=next(n for n in calls if ast.unparse(n.func)=='subprocess.run')
        self.assertEqual(0o027,ast.literal_eval(next(k.value for k in run.keywords if k.arg=='umask')))
        pop=next(n for n in calls if ast.unparse(n.func)=='env.pop')
        self.assertEqual('JAVA_TOOL_OPTIONS',ast.literal_eval(pop.args[0]))
        source=ast.unparse(tree)
        self.assertIn('-Djava.io.tmpdir=',source)
        parent=next(n for n in calls if ast.unparse(n.func)=='os.umask')
        self.assertEqual(0o077,ast.literal_eval(parent.args[0]))

    def test_all_exact_independent_totals_only(self):
        self.assertTrue(complete_result(0,True,[],3576,523,1635))
        baseline=[0,True,[],3576,523,1635]
        mutations={0:[None,True,1,143],1:[None,False,1],2:[None,['flaky'],['missingXML']],3:[None,True,3569,3575,3577],4:[None,True,522,524],5:[None,True,1634,1636]}
        for position,values in mutations.items():
            for value in values:
                changed=list(baseline);changed[position]=value
                with self.subTest(position=position,value=value):self.assertFalse(complete_result(*changed))


if __name__=='__main__':unittest.main()
