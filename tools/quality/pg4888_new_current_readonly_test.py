import copy
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4888_new_current_readonly as role


class Current(unittest.TestCase):
    def test_actual_new_publication_and_full72_reader_not_old_native_credit(self):
        digest=role.context();raw=role.payload()
        for marker in (role.SOURCE,role.BOM,role.AFTER,digest,"'native72Preserved':True","'newRootNotStarted':True","'oldNativeCredit':False",'12884901888'):self.assertIn(marker,raw)
        self.assertEqual(0,check(raw,'<fresh current04bb full reader>'))
        original=json.loads((role.post.role.W/role.post.SLOT/'manifest.safe.json').read_bytes())
        for key,value in [('productionSource',role.post.role.CURRENT),('originalBackupNative72Preserved',False),('newSourceParentNotStarted',False),('newTenReferencesReturnedNormally',False)]:
            bad=copy.deepcopy(original);bad['result'][key]=value
            with self.subTest(key=key),patch.object(role.json,'loads',return_value=bad),self.assertRaises(ValueError):role.context()
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
