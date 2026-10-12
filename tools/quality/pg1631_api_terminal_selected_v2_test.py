"""BUG1141/YKT909: actual selection command and exact independent outcome oracle."""
import ast
import copy
from pathlib import Path
from types import SimpleNamespace
import unittest
import pg1631_api_terminal_selected_v2 as p


class SelectionGateTest(unittest.TestCase):
    def test_actual_gate_rejects_empty_missing_failed_skipped_stale_or_wrong_source(self):
        tree=ast.parse(p.server())
        expression=next(n.value for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='passed')
        code=compile(ast.Expression(expression),'<actual selected outcome gate>','eval')
        expected={'ApiProcessMainTest':4,'ApiProcessLifetimeTest':4,'ApiTerminalCaptureTest':3,'ApiCommittedFatalBindingTest':2}
        base={'r':SimpleNamespace(returncode=0),'EXPECTED':expected,'results':{n:{'tests':v,'failures':0,'errors':0,'skipped':0,'freshAfterBegin':True}for n,v in expected.items()},'static':dict.fromkeys(['protocol','storage','bootstrap','api'],0),'SOURCE':Path('/unused'),'inputs':{'class':'a'},'sha':lambda _: 'a'}
        self.assertTrue(eval(code,base))
        variants=[]
        wrong=copy.deepcopy(base);wrong['results']={};variants.append(wrong)
        wrong=copy.deepcopy(base);wrong['results'].pop('ApiTerminalCaptureTest');variants.append(wrong)
        wrong=copy.deepcopy(base);wrong['r']=SimpleNamespace(returncode=1);variants.append(wrong)
        wrong=copy.deepcopy(base);wrong['inputs']['class']='b';variants.append(wrong)
        wrong=copy.deepcopy(base);wrong['static']['api']=None;variants.append(wrong)
        for key,value in [('tests',0),('tests',14),('failures',1),('errors',1),('skipped',1),('freshAfterBegin',False)]:
            wrong=copy.deepcopy(base);wrong['results']['ApiTerminalCaptureTest'][key]=value;variants.append(wrong)
        for wrong in variants:self.assertFalse(eval(code,wrong))

    def test_compile_only_dependencies_do_not_remove_api_expected_gate(self):
        tree=ast.parse(p.server());assignments={n.targets[0].id:n.value for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)}
        self.assertEqual({'ApiProcessMainTest':4,'ApiProcessLifetimeTest':4,'ApiTerminalCaptureTest':3,'ApiCommittedFatalBindingTest':2},ast.literal_eval(assignments['EXPECTED']))
        self.assertEqual(['protocol','storage','bootstrap','api'],ast.literal_eval(assignments['MODULES']))
        args=assignments['args'];values=[n.value for n in args.elts if isinstance(n,ast.Constant)]
        self.assertEqual(1,values.count('-DfailIfNoTests=false'))
        self.assertIn('-Dsurefire.failIfNoSpecifiedTests=false',values)
        gate=ast.unparse(assignments['passed'])
        for required in ["r.returncode == 0","set(results) == set(EXPECTED)","v['tests'] == EXPECTED[n]","v['failures'] == v['errors'] == v['skipped'] == 0","v['freshAfterBegin']","all((v == 0 for v in static.values()))"]:
            self.assertIn(required,gate)


if __name__=='__main__':unittest.main()
