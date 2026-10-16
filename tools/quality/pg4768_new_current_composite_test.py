"""No historical source in parent18, exact preserved nested SQL/Browser capsules."""
import ast
import inspect
import unittest
from pyflakes.api import check
import pg4752_new_current_admission_image as admission
from pg4752_new_current_admission_test import NewAdmission
import pg4760_new_current_whole_seal as root
import pg4768_new_current_browser_composite as composite
import pg4770_new_current_parent_projection as projection


class Composite(unittest.TestCase):
    def test_exact_capsules_and_chain_never_rebound(self):
        original=root.payload(NewAdmission().binding(),'a'*64)
        chain={'before':{'history':'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'},'after':{},'context':{}}
        raw=composite.compose(original,chain,'b'*64)
        get=lambda text,name:next(ast.literal_eval(n.value)for n in ast.parse(text).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets))
        joined=get(raw,'ORACLE');inner={n.targets[0].id:ast.literal_eval(n.value)for n in ast.parse(joined).body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
        self.assertEqual(chain,inner['CHAIN']);self.assertEqual(get(original,'ORACLE'),inner['ROOT_ORACLE'])
        self.assertEqual(get(original,'GUARD'),get(raw,'GUARD'))
        self.assertIn(root.SLOT+'/before.private.json',joined)
        self.assertEqual(0,check(raw,'<whole browser composite>'))

    def test_projection_exact_source_path_hash_and_no_authority(self):
        raw=projection.payload('a'*64)
        self.assertIn(admission.SOURCE,raw);self.assertIn(admission.BOM,raw);self.assertNotIn(projection.template.SOURCE,raw)
        self.assertIn(composite.SLOT,raw);self.assertIn("EXPECTED='"+'a'*64+"'",raw)
        self.assertIn('len(fields)==18',raw);self.assertNotIn('systemctl',raw)
        host=inspect.getsource(composite.main)
        self.assertLess(host.index("'start.safe.json'"),host.index('child.stdin.write'))
        self.assertIn('child.wait()',host);self.assertNotIn('timeout=',host)


if __name__=='__main__':unittest.main()
