import unittest
from types import SimpleNamespace
import pg5281_factory_finish as role


class StrictPublication(unittest.TestCase):
    def test_proof_rejects_boolean_unknown_wrong_source_or_main(self):
        good={'actualExit':0,'source':'a'*40,'physicalMain':764}
        result={'sourceSnapshot':'a'*40};role.validate_proof(good,result,764)
        for changes in ({'actualExit':False},{'actualExit':1},{'source':'a'*41},
                        {'source':'b'*40},{'physicalMain':763}):
            with self.assertRaises(ValueError):role.validate_proof({**good,**changes},result,764)

    def test_basename_contract_has_no_nested_or_extension_confusion(self):
        self.assertEqual(role.new_files(SimpleNamespace(OUTERS={'A','B'})),{'A.java','B.java'})
        self.assertEqual(role.new_files(SimpleNamespace(OUTERS={'A','A$Nested'},FILES={'A'})),{'A.java'})
        for names in (set(),{'A$Nested'},{'A.java'},{'a/A'}):
            with self.assertRaises(ValueError):role.new_files(SimpleNamespace(OUTERS=names))


if __name__=='__main__':unittest.main()
