import ast
import unittest
from pg1512_original_component_profile_sources import java,refs,PROFILE_JAVA,CLASS,SAVE,TOOLS

class ReadonlyProfileTest(unittest.TestCase):
 def test_fixed_current_source_full_original_and_readonly(self):
  j=java();r=refs();compile(r,'<readonly component profile>','exec')
  self.assertIn(CLASS,j);self.assertIn(SAVE,j);self.assertIn(TOOLS,j)
  self.assertEqual(2,j.count('session.observeStartup(ORIGINAL)'))
  self.assertIn('Pg1512OriginalIoProfile.create()',j)
  self.assertIn('components.safe.jsonl',j)
  self.assertIn('readonly profiler mutation refused',PROFILE_JAVA)
  self.assertIn('readonly profiler identity allocation refused',PROFILE_JAVA)
  self.assertIn('actual.filesystem(p)',PROFILE_JAVA)
  self.assertIn('sec.accessAcl(p,limit)',PROFILE_JAVA)
  self.assertIn('sec.readOnlyFilesystem(p)',PROFILE_JAVA)
  self.assertIn('7cc53215980eadb5d6d788d1df0b997111b3f6beabc6eef4803f4506afb36ea5',r)
  self.assertTrue('value==expected_current and value==snapshot()'in r)
  names=[n.name for n in ast.parse(r).body if isinstance(n,ast.FunctionDef)]
  self.assertNotIn('stop_one',names)
  calls=[n.func.attr for n in ast.walk(ast.parse(r))if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)]
  self.assertNotIn('terminate_once',calls);self.assertNotIn('.revoke(',j);self.assertNotIn('.retire(',j)
if __name__=='__main__':unittest.main()
