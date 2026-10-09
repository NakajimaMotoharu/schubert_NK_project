import ast,unittest
from pg807_parent_observer import watch,files,SOURCE,DIGEST

class Test(unittest.TestCase):
 def test_same_generation_and_no_mutation(self):
  for raw in files().values():ast.parse(raw)
  raw=watch()
  for value in('PG796',"assert role in roots and same(roots[role],aa)","'wholeMorningAccepted':False","'automaticStop':False","deadline=min(deadline,int(m['ExecMainStartTimestampMonotonic'])/1e6+1860)","before==metadata9(ca)"):
   self.assertIn(value,raw)
  self.assertNotIn('PG495',raw);self.assertNotIn('systemctl start',raw)
  self.assertEqual(40,len(SOURCE));self.assertEqual(64,len(DIGEST))

if __name__=='__main__':unittest.main()
