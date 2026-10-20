import hashlib
import unittest
from collections import defaultdict
from pg5876_static3971_join import current_reference


class CurrentXMLProvenanceTest(unittest.TestCase):
    def test_storage_methods_require_unique_actual_current_xml(self):
        ref={'class':'dev.codex.schubert.nk.storage.ResourceScopeTest','method':'unknownCompoundFailures'}
        digest=hashlib.sha256(ref['method'].encode()).hexdigest();row={'class':ref['class'],'caseNameSha256':digest,'xmlSha256':'a'*64,'testId':'PT-WHOLE-'+('b'*64),'result':'PASS_ORIGINAL_XML'};index={(ref['class'],digest):[row]}
        self.assertEqual(row['testId'],current_reference(ref,index)['testId'])
        for bad in({}, {(ref['class'],digest):[row,row]}, {(ref['class'],digest):[{**row,'result':'UNKNOWN'}]}):
            with self.assertRaises(ValueError):current_reference(ref,bad)
        with self.assertRaises(ValueError):current_reference({**ref,'method':'notDeclared'},index)
        duplicate={**index,(ref['class'],hashlib.sha256((ref['method']+'()').encode()).hexdigest()):[row]}
        with self.assertRaises(ValueError):current_reference(ref,duplicate)

    def test_legacy_constructor_and_full_schema_remain_separate(self):
        ref={'class':'dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationExceptionTest','method':'iso009PrimaryAndProtocolAreRequired','designTestId':'PT-JMS-ISO009'}
        digest=hashlib.sha256(ref['method'].encode()).hexdigest();row={'class':ref['class'],'caseNameSha256':digest,'xmlSha256':'a'*64,'testId':'PT-WHOLE-'+('b'*64),'result':'PASS_ORIGINAL_XML'}
        self.assertEqual(row['testId'],current_reference(ref,{(ref['class'],digest):[row]})['testId'])
        with self.assertRaises(ValueError):current_reference({**ref,'designTestId':'PT-JMS-ISO999'},{(ref['class'],digest):[row]})
        full={k:row[k]for k in('class','caseNameSha256','testId','xmlSha256')}
        self.assertEqual(row['testId'],current_reference(full,{(ref['class'],digest):[row]})['testId'])
        with self.assertRaises(ValueError):current_reference(full,defaultdict(list))


if __name__=='__main__':unittest.main()
