import unittest
from pg906_progress_epoch import first_progress
class Test(unittest.TestCase):
 def test_distinct_phases_and_every_broken_join(self):
  old=[{'run_id':'old'+str(i),'count':i}for i in range(4)];first=old+[{'run_id':'current','count':0}]
  self.assertTrue(first_progress(old,first,list(first),'current'))
  for a,b,c,r in ((None,first,first,'current'),(old,old,old,'current'),(old,first,first,None),(old,first,first,'foreign'),(old,first,first+first[-1:],'current'),(old,first,[*old,{'run_id':'current','count':1}],'current'),([*old[:3],{'run_id':'drift'}],first,first,'current')):
   self.assertFalse(first_progress(a,b,c,r))
if __name__=='__main__':unittest.main()
