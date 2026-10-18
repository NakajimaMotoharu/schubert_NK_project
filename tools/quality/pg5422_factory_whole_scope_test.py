import copy
import hashlib
import json
import unittest
from pyflakes.api import checkPath
import pg5422_factory_whole_scope as entry


class WholeScopeBinding(unittest.TestCase):
    def test_actual_current_bindings_preserve_formal_and_native_hold(self):
        values={key:json.loads((entry.ROOT/path).read_bytes()) for key,path in entry.REFS.items()}
        hashes={key:hashlib.sha256((entry.ROOT/path).read_bytes()).hexdigest() for key,path in entry.REFS.items()}
        result=entry.validate(values,hashes)
        self.assertTrue(result['wholeSourceQualified']);self.assertEqual(result['readonlyCandidatesUnknown'],0)
        self.assertFalse(result['formalAccepted']);self.assertFalse(result['newSourceNativeQualified'])
        self.assertEqual(result['acceptedLeafDelta'],0);self.assertIsNone(result['effortPercent'])
        for key,field,bad in [('whole','productionSource','foreign'),('whole','staticSixModules',1),
            ('partition','qualificationSha256','0'*64),('cases','tests',3814),('readonly','readonlyCandidateCount',3),
            ('whole','formalAccepted',True)]:
            invalid=copy.deepcopy(values);invalid[key][field]=bad
            with self.assertRaises(ValueError):entry.validate(invalid,hashes)
        invalid=copy.deepcopy(values);first=next(iter(invalid['selected']['mainDelta']['physicalSha256']))
        invalid['whole']['allPhysicalMainSha256'][first]='0'*64
        with self.assertRaises(ValueError):entry.validate(invalid,hashes)
        for path in (entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
