"""No baseline change/old-parent proof reuse; strict same actual source runtime join."""
import ast,unittest
from pg849_a01_current import code
class Test(unittest.TestCase):
 def test_current_identity_driver_and_original_budget(self):
  raw=code();ast.parse(raw)
  for v in('2a0d5aa392c85a1dc12a1cdb423978e8500895b8','8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977','PG832','pg844-external-once-v1','pg843-parent-watch-v1.private.jsonl','pg842-resume-post-v1.exit','CHR-A01.json','NativeNkA01Capture','1800000000',"'fullGate':False","'rawCookieTokenExported':False"):self.assertIn(v,raw)
  for v in('PG750','pg758','pg759','pg760','systemctl start','systemctl stop'):self.assertNotIn(v,raw)
  self.assertIn('sameCapturedParentApiWebCaddyBeforeAfter',raw)
if __name__=='__main__':unittest.main()
