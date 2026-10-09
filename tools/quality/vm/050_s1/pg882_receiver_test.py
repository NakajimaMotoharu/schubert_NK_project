"""Independent full once body/fsync fixture; fake start client, no VM/service authority."""
import ast,datetime,hashlib,json,os,pathlib,subprocess,tempfile,types,unittest
from unittest.mock import patch
import pg882_ordinary_once as p
import pg880_ordinary_before as previous
class Test(unittest.TestCase):
 def test_body_reserves_once_then_persists_issued_without_stopped_recheck(self):
  proof,seals,prefix=previous.inputs()
  with patch.object(p,'inputs',return_value=(proof,seals,prefix)),patch.object(p.Path,'read_bytes',return_value=b'{"actualExit":0,"beforeSha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}'):
   tree=ast.parse(p.payload())
  region=next(n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body))
  start=next(i for i,n in enumerate(region.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='before_raw'for t in n.targets))
  code=ast.Module(body=region.body[start:],type_ignores=[])
  with tempfile.TemporaryDirectory(prefix='pg882-body-fixture-')as directory:
   root=pathlib.Path(directory);before={'ordinaryNoargs':True,'oldOriginalCompleted':True,'priorNewGenuine':True};golden=json.dumps(before,sort_keys=True).encode();(root/'before.json').write_bytes(golden)
   native=root/'native';native.mkdir();(native/'fixture.exec').write_bytes(b'independent harmless fixture only')
   save=root/'once';state={'started':False,'calls':[],'snapshots':0}
   class Paths(ast.NodeTransformer):
    def visit_Constant(self,n):
     value={'/var/lib/pgpt-s1-preservation/pg880-ordinary-before-v1/after.private.json':str(root/'before.json'),'/var/lib/pgpt-s1-preservation/pg882-ordinary-once-v1':str(save),'/run/schubert-nk/pt-coverage':str(native),'/var/lib/schubert-nk/maintenance/active':str(root/'active'),'a'*64:hashlib.sha256(golden).hexdigest()}.get(n.value,n.value)if isinstance(n.value,str)else n.value
     return ast.copy_location(ast.Constant(value),n)
   code=Paths().visit(code);ast.fix_missing_locations(code)
   def snapshot():
    if state['started']:raise AssertionError('post-start precondition is forbidden')
    state['snapshots']+=1;return before
   def run(args,**kw):
    self.assertEqual(args,['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'])
    self.assertTrue((save/'external-start-guard.private.json').is_file());self.assertFalse((save/'external-start-issued.private.json').exists());self.assertFalse(state['started'])
    state['started']=True;state['calls'].append(args);return types.SimpleNamespace(returncode=0)
   def check_output(args,**kw):
    self.assertTrue(state['started']);self.assertEqual(args[:3],['/usr/bin/systemctl','show','schubert-nk-morning-controller.service'])
    return 'InvocationID=0123456789abcdef0123456789abcdef\nMainPID=1234\nJob=2345\nExecMainStartTimestampMonotonic=3456\n'
   namespace={'pathlib':pathlib,'hashlib':hashlib,'json':json,'os':os,'datetime':datetime,'standard_snapshot':snapshot,'subprocess':types.SimpleNamespace(run=run,check_output=check_output,PIPE=subprocess.PIPE)}
   exec(compile(code,'<independent actual filesystem once-body fixture>','exec'),namespace)
   issued=json.loads((save/'external-start-issued.private.json').read_bytes());guard=json.loads((save/'external-start-guard.private.json').read_bytes())
   self.assertEqual(issued['clientExit'],0);self.assertEqual(issued['MainPID'],'1234');self.assertEqual(len(state['calls']),1);self.assertEqual(state['snapshots'],2)
   self.assertTrue(guard['repeatForbidden']);self.assertEqual(guard['beforeSha256'],hashlib.sha256(golden).hexdigest());self.assertTrue(issued['clientSuccessIsNotParentSuccess'])
   self.assertEqual((save/'native-before/fixture.exec').read_bytes(),b'independent harmless fixture only')
if __name__=='__main__':unittest.main()
