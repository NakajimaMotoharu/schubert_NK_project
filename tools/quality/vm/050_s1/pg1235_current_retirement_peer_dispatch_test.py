import unittest
import pg1235_current_retirement_peer_dispatch as p
import pg1234_current_retirement_peer_preflight as pre
import pg1233_completed_retirement_peer_compile as compiler

class CurrentPeerTest(unittest.TestCase):
    def test_whole_factory_closure_and_exact_new_paths(self):
        env={'__file__':p.__file__,'__name__':'qualified_new_retirement'}
        s=p.source();exec(compile(s,'<actual new dispatcher namespace>','exec'),env)
        self.assertEqual(env['GUEST'],'/var/lib/pgpt-s1-preservation/pg1232-native-tools-v1')
        self.assertTrue('Pg1232NativeStop retire'in s)
        self.assertTrue("pre['fixedOldRecoveryPostVerified']"in s)
        compile(env['STAGE'],'<actual new immutable archive>','exec')
        for n,v in env['generate'](env['proof']()).items():
            self.assertFalse('pg1224-native-tools'in v,n)
            if n.endswith('.py'):compile(v,'<actual new generated '+n+'>','exec')
        compile(pre.payload(),'<actual fixed-owner-free preflight>','exec')
        c={'__name__':'qualified_peer_compiler','__file__':compiler.__file__};exec(compile(compiler.source(),'<actual new compiler namespace>','exec'),c)
        self.assertTrue('pg1231-current-retirement-handoff-v1.safe.json'in compiler.source())

if __name__=='__main__':unittest.main()
