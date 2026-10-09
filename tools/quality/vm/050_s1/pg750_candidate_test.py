"""Independent literal closed byte changes and each module perturbation; never signs."""
import ast
import copy
import unittest
from pg749_candidate_contract import MODULES,CHANGED,ADDED,verify_delta
from pg750_candidate_build import source


class Test(unittest.TestCase):
    def fixture(self):
        old={m:{'literal/'+m+'.class':'0'*64}for m in MODULES}
        for m,names in CHANGED.items():
            for n in names:old[m][n]='0'*64
        new=copy.deepcopy(old)
        for m,names in CHANGED.items():
            for n in names:new[m][n]='1'*64
        for m,names in ADDED.items():
            for n in names:new[m][n]='2'*64
        return old,new

    def test_exact_seven_two_and_all_module_perturbations(self):
        old,new=self.fixture();self.assertEqual(15,verify_delta(old,new))
        self.assertEqual(7,sum(map(len,CHANGED.values())));self.assertEqual(2,sum(map(len,ADDED.values())))
        for m in MODULES:
            for mode in ('change','add','remove','digest'):
                altered=copy.deepcopy(new);n='literal/'+m+'.class'
                if mode=='change':altered[m][n]='9'*64
                elif mode=='add':altered[m]['foreign.class']='3'*64
                elif mode=='remove':del altered[m][n]
                else:altered[m][n]='UNKNOWN'
                with self.subTest(module=m,mode=mode),self.assertRaises(ValueError):verify_delta(old,altered)
        for m,names in ADDED.items():
            for n in names:
                altered=copy.deepcopy(new);del altered[m][n]
                with self.assertRaises(ValueError):verify_delta(old,altered)
        for invalid in (None,{}, {'api':None}):
            with self.assertRaises(ValueError):verify_delta(old,invalid)

    def test_source_host_current_and_validation_before_signature(self):
        raw=source();ast.parse(raw)
        for value in ('pg748-closing-six-host-v1','pg750-release-v1','pg715-release-v1','3513','519','1616',
            '8d4b68b4f1449932ebe506aaf08e584bbfea8dd2','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172',
            'd4d3ba09651c75d15334e2775fa9a1ae8f8362e2fa92d9e8ebb57c1d8667d96e',
            '74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5'):
            self.assertIn(value,raw)
        self.assertLess(raw.index('verify_delta(old_classes, new_classes)'),raw.index("'-sign'"))
        self.assertNotIn('pg631-release-v1',raw)
        self.assertIn("{'VERSION', 'api/api.jar'} <= changed",raw)


if __name__=='__main__':unittest.main()
