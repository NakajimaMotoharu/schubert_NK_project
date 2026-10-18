import copy
import inspect
import json
import unittest
from pyflakes.api import checkPath
import pg5430_ownership_signed_candidate as entry


class SignedCandidate(unittest.TestCase):
    def test_current_whole_native_formal_holds_and_all_declared_case_identities(self):
        outer=json.loads((entry.W/entry.SLOT/'manifest.safe.json').read_bytes())
        gate=entry.validate_gate(outer,entry.SOURCE)
        self.assertEqual(gate['mainClasses'],1664);self.assertFalse(gate['formalAccepted'])
        for field,value in [('tests',3895),('mainClasses',1650),('F03Accepted',True),('global100',True),
            ('oldNativeImported',True),('allSixFormatBeforeAnyPt',False),('newCases',[])]:
            wrong=copy.deepcopy(outer);wrong['result'][field]=value
            with self.assertRaises(ValueError):entry.validate_gate(wrong,entry.SOURCE)
        self.assertTrue(entry.qualification_matches(outer))

    def test_actual_signed_a2_to_current_delta_never_uses_whole_old1654_as1650(self):
        old=json.loads((entry.W/'pg4970-ssc304-whole-qualified-v1/manifest.safe.json').read_bytes())['result']['allPhysicalMainSha256']
        new=json.loads((entry.W/entry.SLOT/'manifest.safe.json').read_bytes())['result']['allPhysicalMainSha256']
        before,after=entry.grouped(old),entry.grouped(new)
        actual=entry.delta(before,after,old,new)
        self.assertEqual((len(actual['added']),len(actual['removed']),actual['oldPhysicalMain'],actual['newPhysicalMain']),(15,1,1650,1664))
        wrong=copy.deepcopy(after);module=next(module for module in wrong if wrong[module]);name=next(iter(wrong[module]));wrong[module][name]='0'*64
        with self.assertRaises(ValueError):entry.delta(before,wrong,old,new)
        with self.assertRaises(ValueError):entry.delta(before,after,new,new)

    def test_source_version_and_new_only_signature_names_are_exact_without_guest_authority(self):
        raw=entry.main_source();compile(raw,'<complete candidate body>','exec')
        for literal in ('pg5430-candidate-build-v1.safe.json',"data['release'] == '0.1.0-PG4980'",'0.1.0-PG5430',
            'pg5416-ownership-whole-qualified-v2',"verify_delta(before, after) == 1664",'PGPT_QUALIFICATION_ONLY',
            "'addedClasses': 15","'removedClasses': 1","'oldPhysicalMain': 1650","'deploymentAuthority': False"):
            self.assertIn(literal,raw)
        self.assertNotIn('0.1.0-PG4860',raw)
        self.assertIn('openssl',raw);self.assertNotIn('systemctl',raw);self.assertNotIn('stage-place',raw)
        for path in (entry.__file__,__file__):self.assertEqual(checkPath(path),0)
        self.assertIn("contract['readonlyCandidatesUnknown']==0",inspect.getsource(entry.main))


if __name__=='__main__':unittest.main()
