"""Actual main/operation/helper/CP/bus/fullscope bindings are coherent."""
import ast
import unittest
import pg1381_role_failed_ref_pair_proof as p

class Test(unittest.TestCase):
    def test_whole_current_role_pair_generation(self):
        raw=p.payload(dict.fromkeys(p.previous.previous.previous.previous.prior.prior.previous.transport.previous.SEALS,'b'*64));tree=ast.parse(raw)
        candidate=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='candidate')
        scope={};exec(compile(ast.Module(body=[candidate],type_ignores=[]),'<actual role candidate>','exec'),scope)
        argv=b'/opt/jdk-25.0.4/bin/java\0-cp\0EXACT\0Pg1374BootstrapRolePreparation\0prepare\0'
        self.assertTrue(scope['candidate'](argv,'/opt/jdk-25.0.4/bin/java'))
        self.assertFalse(scope['candidate'](argv.replace(b'prepare',b'verify'),'/opt/jdk-25.0.4/bin/java'))
        for required in ('pg1374-bootstrap-role-tools-v2','pg1374_bootstrap_role_refs.py','pg1374-bootstrap-role-prepare-v1',"'refs.private.log'",'PG1381-role-failed-ref-pair-v1','len(names)==1'):
            self.assertTrue(required in raw,required)
        self.assertFalse('Pg1362BootstrapExisting'in raw)
        self.assertFalse('pidfd_send_signal'in raw)

if __name__=='__main__':unittest.main()
