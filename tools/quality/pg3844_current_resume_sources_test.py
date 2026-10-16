import ast
import unittest
import pg3844_current_resume_sources as tool


class ResumeRoles(unittest.TestCase):
    def test_current_full11_and_latest_tuple_without_historical_fixture_rewrite(self):
        values=tool.sources();self.assertEqual(20,len(values));raw='\n'.join(values.values())
        for marker in [tool.SOURCE,tool.BOM,tool.BEFORE,tool.BASELINE,tool.RUN,tool.TOOLS,tool.SAVE,'--resume']:self.assertTrue(marker in raw,marker)
        for marker in ['PG3420','pg3564','Pg3564',tool.previous.BEFORE]:self.assertFalse(marker in raw,marker)
        original=tool.pinned(tool.CURRENT,'Pg3822OriginalTupleTest.java').replace('Pg3822NativeStop',tool.CLASS).replace('Pg3822','Pg3844').replace('PG3822','PG3844')
        self.assertEqual(original,values['Pg3844OriginalTupleTest.java'])
        native=ast.parse(values['pg3844_native_refs.py']);assigned={n.targets[0].id:ast.literal_eval(n.value)for n in native.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in {'INV','START','END'}}
        self.assertEqual({'INV':'6f7821fe0af24d95953a9e29abd00c0d','START':110588829449,'END':112347576550},assigned)


if __name__=='__main__':unittest.main()
