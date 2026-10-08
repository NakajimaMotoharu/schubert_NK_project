"""Fixed real cohort source binding. No VM/ownership actions."""
import ast
from pathlib import Path
import unittest
R=Path(__file__).resolve().parent


class Test(unittest.TestCase):
    def test_actual_end_and_baseline_are_literal_and_not_unbound(self):
        text=(R/'pg611_native_refs.py').read_text();tree=ast.parse(text)
        v={t.id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)for t in n.targets
           if isinstance(t,ast.Name)and t.id in ('START','END','BASELINE_SHA','INV')}
        self.assertEqual(v,{'START':86264628081,'END':87761979588,
            'BASELINE_SHA':'8d9888702641b29b9feff811cebc94f86d97de96330a43fb0c29c6959f98bf47',
            'INV':'5a1acaa0c35e484c979401e3b6dfb36a'})
        self.assertIn('pg609-completed-readonly-v1/before.private.json',text)
        self.assertIn('pg604-completed-activate-v1/after.private.json',text)
        self.assertIn('stages==h.ORDER',text);self.assertIn('all(now[k]==first[k]',text)

    def test_actual_backend_four_generations(self):
        tree=ast.parse((R/'pg611_native_owned_stop.py').read_text())
        v=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)
               and any(isinstance(t,ast.Name)and t.id=='EXPECTED'for t in n.targets))
        self.assertEqual(v,{'caddy.service':('1460173','fd0cd00933ce43b88634c43faef7a0ef'),
            'schubert-nk-web.service':('1454010','866af4c303904f1e998a5a50f6ccc716'),
            'schubert-nk-api.service':('1451527','4db7f8a4637a4b9f909de4d319677179'),
            'artemis.service':('1304653','1a7bc5e9a7734bbb9a657bf11fac7dbe')})
        self.assertEqual((R/'pg611_parent_receipt.py').read_text(),(R/'pg609_parent_receipt.py').read_text())

    def test_native_driver_is_closed_newonly_inventory_and_current_release(self):
        s=(R/'pg611_native_stop_v1.py').read_text();ast.parse(s)
        self.assertIn("len(files)==8",s);self.assertIn('PG600/operations/batch.jar',s)
        self.assertIn("['git','status','--porcelain']",s)
        self.assertIn('PG611_EXPIRY_REFERENCE_ORACLE independentAssertions=55',s)
        self.assertIn('8d9888702641b29b9feff811cebc94f86d97de96330a43fb0c29c6959f98bf47',s)
        for path in ('pg611_native_owned_stop.py','pg611_native_refs.py','pg611_parent_receipt.py','Pg611NativeStop.java'):
            text=(R/path).read_text()
            for old in ('b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e','57f0e73d-d334-4882-9284-04246011da54',
                        '267003d6e12845dd8690cd9bd5afcad0','PG548','59234299','57679957905'):
                self.assertNotIn(old,text)


if __name__=='__main__':unittest.main()
