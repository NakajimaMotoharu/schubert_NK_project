import ast
import copy
import hashlib
import pathlib
import stat
import unittest
import pg799_pending_sources as p

class Test(unittest.TestCase):
    def test_independent_publication_vector(self):
        env={'hashlib':hashlib,'pathlib':pathlib,'stat':stat};exec(compile(p.approval_oracle(),'<isolated delta>', 'exec'),env)
        expected=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG796\nmanifest_sha256=c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d\n';self.assertEqual(expected,env['NEW_APPROVAL'])
        root='/etc/schubert-nk/release-approval';file=root+'/current'
        def item(ino,mode,size,digest):return {'metadata':[2,ino,0,0,mode,1,size,7,8],'sha256':digest}
        old={root:{root:item(10,0o40700,4096,None),file:item(11,0o100400,len(expected),'old')}}
        after=copy.deepcopy(old);after[root][file]=item(12,0o100400,len(expected),hashlib.sha256(expected).hexdigest());after[root][root]['metadata'][7:]=[10,11]
        self.assertTrue(env['approval_only'](old,after))
        for index in (0,2,3,4,5,6):
            bad=copy.deepcopy(after);bad[root][file]['metadata'][index]+=1;self.assertFalse(env['approval_only'](old,bad))
        for bad in ({},{root:{}},{root:{**after[root],root+'/extra':item(13,0o100400,1,'extra')}}):self.assertFalse(env['approval_only'](old,bad))
        bad=copy.deepcopy(after);bad[root][file]['sha256']='foreign';self.assertFalse(env['approval_only'](old,bad))
    def test_full_pending_assembly(self):
        for py in (p.snapshot_library(),p.refs(),p.before_freeze()):ast.parse(py)
        raw=p.java()
        for value in (p.SOURCE,p.DIGEST,p.OLD_DIGEST,'9de2d03c-28c7-4647-97d9-c66ace06048c','021111b4-6de5-4733-917d-5ac176240ffc','pg799_pending_refs.py','pg799_before_freeze.py','pg799-pending-tools-v1','lease.confirmClosed()','pulse();phase="REFERENCE_SCOPE"'):
            self.assertIn(value,raw)
        for value in ('files.revoke(','.retirePair(','.stop(','Pg490','PG495','PG489','pg498','helper("stop:'):
            self.assertNotIn(value,raw)
        self.assertIn('pg800-probe-post-v1/after.private.json',p.snapshot_library())
        self.assertIn('with CaptureReferences():',p.refs());self.assertIn("phase!=b'release'",p.refs())
    def test_complete_transport_and_place_surface(self):
        from pg799_pending_native import source
        from pg799_candidate_place import PAYLOAD
        raw=source();ast.parse(raw);ast.parse(PAYLOAD)
        self.assertIn("sys.argv[1]in ('stage','activate')",raw)
        literal_argv=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)and isinstance(n.value,str)]
        self.assertIn('Pg799PendingDeployment '+p.SOURCE+' '+p.DIGEST,literal_argv)
        self.assertIn('pg799-candidate-place-v1.exit',raw)
        self.assertIn('pg799-pending-tools-v1',raw)
        self.assertNotIn("if action=='recover'",raw)
        self.assertNotIn('Pg778',raw)
        self.assertNotIn('systemctl',PAYLOAD)
    def test_refs_held_during_whole_prefreeze_capture_and_new_v2(self):
        from pg799_pending_v2 import compile_source,native_source
        from pg801_guard_handoff import payload
        ast.parse(compile_source());ast.parse(native_source());ast.parse(payload())
        tree=ast.parse(p.before_freeze());scope=next(n for n in tree.body if isinstance(n,ast.With))
        self.assertTrue(any(isinstance(n,ast.For)for n in scope.body))
        self.assertIn('CaptureReferences()',ast.unparse(scope.items[0].context_expr))
        self.assertIn('pg799-pending-tools-v2',native_source());self.assertIn('pg799-frozen-v2.safe.json',compile_source())
        self.assertNotIn('SIGKILL',payload());self.assertIn('signal.SIGTERM',payload())

if __name__=='__main__':unittest.main()
