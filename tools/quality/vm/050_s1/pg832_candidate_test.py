"""Independent literal namespace/delta and preserved-source qualification oracle."""
import ast
import unittest
from pg832_candidate_contract import MODULES,CHANGED,ADDED,verify_delta
from pg832_candidate_build import source
class Test(unittest.TestCase):
    def test_closed_two_changes_twelve_additions_and_every_foreign_module(self):
        old={m:{'literal.class':'1'*64}for m in MODULES}
        old['batch'].update({n:'2'*64 for n in CHANGED['batch']})
        new={m:dict(v)for m,v in old.items()}
        new['batch'].update({n:'3'*64 for n in CHANGED['batch']})
        new['batch'].update({n:'4'*64 for n in ADDED['batch']})
        self.assertEqual(2,len(CHANGED['batch']));self.assertEqual(12,len(ADDED['batch']))
        self.assertEqual(20,verify_delta(old,new))
        for module in MODULES:
            bad={m:dict(v)for m,v in new.items()};bad[module]['literal.class']='5'*64
            with self.assertRaises(ValueError):verify_delta(old,bad)
        for name in ADDED['batch']:
            bad={m:dict(v)for m,v in new.items()};bad['batch'].pop(name)
            with self.assertRaises(ValueError):verify_delta(old,bad)
        for name in CHANGED['batch']:
            bad={m:dict(v)for m,v in new.items()};bad['batch'][name]='2'*64
            with self.assertRaises(ValueError):verify_delta(old,bad)
        with self.assertRaises(ValueError):verify_delta(None,new)
        raw=source();ast.parse(raw)
        for literal in ('pg796-release-v1','pg832-release-v1','pg830-manager-six-host-v1',
            "SOURCE = '2a0d5aa392c85a1dc12a1cdb423978e8500895b8'",
            "OLD_SOURCE = '102cdf1d365ab321f74b523237590eee764ae858'",
            "gate['tests'] == 3534","gate['suites'] == 522","gate['mainClasses'] == 1632",
            "'addedAbstractInterfaces': 6, 'addedInternalClasses': 4, 'addedOuterClasses': 2"):
            self.assertIn(literal,raw)
        self.assertNotIn('NEXT_',raw)
if __name__=='__main__':unittest.main()
