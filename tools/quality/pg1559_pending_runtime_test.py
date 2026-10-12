"""Independent literal, actual generated configuration and all real FD IO faults."""
import ast
import copy
from pathlib import Path
import types
import unittest
from pg1559_pending_runtime_sources import java,refs,writer,RUN

class RuntimeTest(unittest.TestCase):
    def test_writer_literal_and_all_real_fd_io_faults(self):
        module=types.ModuleType('fixed_current_writer');exec(writer(),module.__dict__)
        text=Path(__file__).parent.joinpath('vm/050_s1/pg1160_runtime_writer_test.py').read_text().replace('import pg1160_runtime_writer as writer','').replace('343a5a1b-d064-47d5-88c2-31c36d7ba7a4',RUN)
        tree=ast.parse(text);nodes=[n for n in tree.body if not isinstance(n,ast.If)]
        env={'writer':module};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<new current literal/fault tests>','exec'),env)
        result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromTestCase(env['WriterTest']).run(result)
        self.assertEqual(result.testsRun,3);self.assertEqual(result.errors,[]);self.assertEqual(result.failures,[])
        self.assertEqual(module.NAME,'zz-pg1160-once-resume.conf');self.assertEqual(module.RUN_ID,'15700a87-9117-4f63-a0ff-768dd604d0f1')

    def test_actual_effective_configuration_and_negative(self):
        tree=ast.parse(refs());names={'require','exec_record','configuration_permitted'}
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names or isinstance(n,ast.Import)and any(a.name=='re'for a in n.names)]
        morning='schubert-nk-morning-controller.service';root=Path('/run/systemd/system')
        def decl(argv):return '{ path=/usr/bin/java ; argv[]='+argv+' ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'
        old={'ExecStart':decl('/usr/bin/java literal-agent'),'DropInPaths':'/etc/native/pg477-native-coverage.conf','Other':'fixed'}
        expected=copy.deepcopy(old);expected['ExecStart']=decl('/usr/bin/java literal-agent --resume 15700a87-9117-4f63-a0ff-768dd604d0f1');expected['DropInPaths']+=' /run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg1160-once-resume.conf'
        env={'runtime_changed':True,'MORNING':morning,'RUNTIME':root,'profile_expected':{'configuration':{morning:old}},'writer':types.SimpleNamespace(UNIT='schubert-nk-morning-controller.service.d',NAME='zz-pg1160-once-resume.conf',RUN_ID=RUN)}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual effective configuration gate>','exec'),env);env['configuration_permitted'](morning,expected)
        for key,value in [('ExecStart',decl('/usr/bin/java literal-agent')),('ExecStart',None),('DropInPaths','foreign'),('Other','changed')]:
            bad=copy.deepcopy(expected);bad[key]=value
            with self.assertRaises(ValueError):env['configuration_permitted'](morning,bad)
        env['runtime_changed']=False;env['configuration_permitted'](morning,old)
        with self.assertRaises(ValueError):env['configuration_permitted'](morning,expected)

    def test_composed_binding_readcommitted_no_business_start(self):
        j=java();s=refs();ast.parse(s)
        for literal in ['database.setReadOnly(false)','TRANSACTION_READ_COMMITTED','PG271-runtime-once','allScopesReturnedNormally=true']:
            self.assertIn(literal,j)
        for banned in ['.invalidate(','.revoke(','StartUnit','StopUnit','UUID.randomUUID']:self.assertNotIn(banned,j+s)
        self.assertEqual(s.count("command(['/usr/bin/systemctl','daemon-reload'],4096)"),1)
        self.assertIn('initialize_runtime();first=verify_current()',s);self.assertIn('inventory_check();return value',s)

if __name__=='__main__':unittest.main()
