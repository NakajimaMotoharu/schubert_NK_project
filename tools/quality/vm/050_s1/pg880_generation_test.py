"""Whole independent capture/once scopes and reservation-before-start policy."""
import ast,unittest
from unittest.mock import patch
import pg880_ordinary_before as p
class Test(unittest.TestCase):
 def test_capture_ast_and_full_scope(self):
  proof,seals,prefix=p.inputs();raw=p.payload(proof,seals);tree=ast.parse(raw)
  defs={n.name for n in tree.body if isinstance(n,ast.FunctionDef)}
  self.assertIn('standard_snapshot',defs);self.assertIn('tree_snapshot',defs)
  for v in('list(metadata9(s))','pg880-ordinary-before-v1','priorNewGenuine',"snapshot_raw=json.dumps(value,sort_keys=True).encode()"):
   self.assertIn(v,raw)
  self.assertNotIn('systemctl\',\'start',raw)
 def test_once_ast_newonly_no_replay(self):
  import pg882_ordinary_once as once
  proof,seals,prefix=p.inputs()
  fixture={'actualExit':0,'beforeSha256':'a'*64}
  with patch.object(once,'inputs',return_value=(proof,seals,prefix)),patch.object(once.Path,'read_bytes',return_value=b'{"actualExit":0,"beforeSha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}'):
   raw=once.payload()
  ast.parse(raw)
  self.assertEqual(raw.count("subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']"),1)
  self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("subprocess.run(['/usr/bin/systemctl','start'"))
  for v in('pg880-ordinary-before-v1','pg882-ordinary-once-v1',"require(value==standard_snapshot())",'manager.LoadUnit(u);manager.RefUnit(u)',"for u in reversed(refs):manager.UnrefUnit(u)"):
   self.assertIn(v,raw)
  for v in ('pg872-ordinary-once-v1','with StageReferences','protected()','standard_snapshot(limited)'):
   self.assertNotIn(v,raw)
if __name__=='__main__':unittest.main()
