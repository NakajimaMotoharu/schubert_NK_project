import ast
import unittest
from pg1257_fresh_independent_terminal_post import payload

class FreshIndependentTerminalPostTest(unittest.TestCase):
    def test_actual_generated_complete_current_binding_and_data_equality(self):
        seals={k:str(n)*64 for n,k in enumerate(['before.private.json','after.private.json','complete.private','parent.private.jsonl'],1)}
        s=payload(seals);t=ast.parse(s);compile(s,'<actual whole current independent post>','exec')
        names={n.name for n in t.body if isinstance(n,ast.FunctionDef)}
        self.assertIn('require',names)
        self.assertNotIn('a14cc600a4fd4f2e9d8c4731ad9d754b',s)
        self.assertNotIn('343a5a1b-d064-47d5-88c2-31c36d7ba7a4',s)
        self.assertIn('62400649336',s);self.assertIn('pg1253-native-stop-v1',s)
        self.assertIn('all24UnchangedTwice',s);self.assertIn('allClientAdvisoryFlock0',s)
        for bad in [{},None,dict(seals,extra='a'*64),dict(seals,**{'before.private.json':'z'*64})]:
            with self.assertRaises(ValueError):payload(bad)
        node=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='require')
        ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual postcondition assertion>','exec'),ns)
        ns['require'](True)
        with self.assertRaises(ValueError):ns['require'](False)

if __name__=='__main__':unittest.main()
