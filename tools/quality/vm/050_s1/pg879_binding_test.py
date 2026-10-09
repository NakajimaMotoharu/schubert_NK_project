"""Native proof/bounds/host closure; pure source construction not execution authority."""
import ast,unittest
import pg879_native_counter as p
class Test(unittest.TestCase):
 def test_new_source_cohort_only(self):
  raw=p.code({'fixture':'c'*64},'a'*64,'b'*64);ast.parse(raw)
  for v in(p.SOURCE,'pg877-native-stop-v1','pg878-terminal-final-v1','pg857-completed-reference-six-host-v1','pg879-current-eight-native-v1','183192933299','184317014132','09167719cb0445fea8da5a6fdbaa3b0f','189291',"tests']==3541",'classByteMismatch','len(info)==1','fcc7df91f91af8867e2c911fd54e7a834c6d3ef313fc028be0d8c9f417e0d6c6'):
   self.assertIn(v,raw)
  for v in ('pg630','pg642','pg644','36fe7a0b','pg599','23b14a44','104329','293d218b','formalAccepted\':True'):
   self.assertNotIn(v,raw)
 def test_catalog_new_seal(self):
  raw=p.catalog('a'*64);ast.parse(raw)
  self.assertIn('pg877-native-stop-v1',raw);self.assertIn('a'*64,raw)
  self.assertIn("assert len(result)==8",raw)
if __name__=='__main__':unittest.main()
