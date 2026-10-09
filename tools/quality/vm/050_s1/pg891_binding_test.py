"""Second fixed epoch end/bounds + stop/collection gate closure, no execution."""
import ast,unittest
import pg887_compile as compile_tool,pg887_native_stop as stop,pg890_terminal_final as final,pg891_native_counter as counter
class Test(unittest.TestCase):
 def test_whole_fixed_surface(self):
  for p in (compile_tool,stop,final):ast.parse(p.source())
  raw=stop.source();self.assertIn('pg885-completed-readonly-v1',raw);self.assertIn('pg884-chr-a01-native-v1',raw);self.assertNotIn('pg875-',raw)
  self.assertIn('pg887-stop-v1.exit',final.source());self.assertIn('pg885-completed-readonly-v1',final.source())
  raw=counter.code({'fixture':'c'*64},'a'*64,'b'*64,186700000000);ast.parse(raw)
  for v in ('pg887-stop-v1.exit','pg890-terminal-final-v1','pg891-current-eight-native-v1','75f48ce36cd740e98a801eede7fdbb7f','186700000000','185542282251','pg857-completed-reference-six-host-v1'):
   self.assertIn(v,raw)
  for old in ('pg877','pg878','pg879','184317014132','183192933299'):self.assertNotIn(old,raw)
 def test_end_foreign_or_outside_original_budget(self):
  for end in (None,True,185542282250,187342282252):
   with self.assertRaises(AssertionError):counter.code({},'a'*64,'b'*64,end)
if __name__=='__main__':unittest.main()
