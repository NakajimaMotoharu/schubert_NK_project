import ast
import copy
from pathlib import Path
import types
import unittest
from pg1172_runtime_sources import files,BASE,HASH


class CorrectRuntimeTest(unittest.TestCase):
    def test_current_same_directory_correct_effective_declaration(self):
        v=files();s=v['pg1172_runtime_refs.py'];ast.parse(s)
        for p in [BASE,HASH,'runtime.owned_prepare(','left[1]+\' --resume \'+runtime.RUN_ID','m[:6]==runtime_parent[:6]',"str(RUNTIME/runtime.NAME)",'runtime_tree()','manager.UnrefUnit(u)']:
            self.assertTrue(p in s,p)
        w=v['pg1172_runtime_writer.py'];ast.parse(w)
        self.assertTrue("NAME='zz-pg1160-once-resume.conf'"in w)
        self.assertFalse('os.mkdir('in w)
        self.assertTrue('pg1172-runtime-resume-v1'in v['Pg1172RuntimeResume.java'])

    def test_generated_changed_branch_imports_and_independent_literal(self):
        s=files()['pg1172_runtime_refs.py'];t=ast.parse(s)
        nodes=[n for n in t.body if isinstance(n,ast.Import)and any(a.name=='re'for a in n.names)or isinstance(n,ast.FunctionDef)and n.name in {'exec_record','require','require_runtime_configuration'}]
        morning='schubert-nk-morning-controller.service';directory=Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
        def decl(argv):return '{ path=/usr/bin/java ; argv[]='+argv+' ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'
        before={morning:{'ExecStart':decl('/usr/bin/java literal-agent'), 'DropInPaths':'/etc/native/pg477-native-coverage.conf','Other':'fixed'}}
        gold=copy.deepcopy(before);gold[morning]['ExecStart']=decl('/usr/bin/java literal-agent --resume 343a5a1b-d064-47d5-88c2-31c36d7ba7a4');gold[morning]['DropInPaths']+=' '+str(directory/'zz-pg1160-once-resume.conf')
        env={'baseline':{'configuration':before},'changed':True,'MORNING':morning,'RUNTIME':directory,'runtime':types.SimpleNamespace(RUN_ID='343a5a1b-d064-47d5-88c2-31c36d7ba7a4',NAME='zz-pg1160-once-resume.conf')}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual generated changed branch>','exec'),env)
        env['require_runtime_configuration'](gold)
        for key,value in [('ExecStart',decl('/usr/bin/java literal-agent')),('ExecStart',None),('DropInPaths','foreign'),('Other','changed')]:
            bad=copy.deepcopy(gold);bad[morning][key]=value
            with self.assertRaises(ValueError):env['require_runtime_configuration'](bad)


if __name__=='__main__':unittest.main()
