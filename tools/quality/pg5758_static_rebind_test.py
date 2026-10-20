"""Source/byte/ambiguity negative fixtures; no Production PT, host or native operations."""
import hashlib
import unittest
from pg5758_static_rebind import bind_one


class ExactRebindTest(unittest.TestCase):
    def inputs(self):
        raw=b'package p;\npublic class C {}\n';digest=hashlib.sha256(raw).hexdigest()
        current={'sourcePath':'src/schubert-nk-api/src/main/java/p/C.java','sourceSha256':digest,'findingId':'current','rule':'X','beginline':'2','endline':'2','begincolumn':'1','endcolumn':'4','status':'NOT_REVIEWED_CURRENT_SOURCE'}
        old={**current,'findingId':'historical','status':'REQUIRED_CONTRACT','reason':'explicit prior rationale','wholeCaseRefs':[{'testId':'old-case','xmlSha256':'old-xml'}]}
        classes={'api:p/C.class':'a'*64}
        return current,old,raw,classes

    def test_exact_binding_keeps_historical_test_out_of_current_pass(self):
        c,o,raw,classes=self.inputs();row,kind=bind_one(c,[o],raw,classes,classes)
        self.assertEqual('REBOUND',kind);self.assertEqual('current',row['findingId']);self.assertEqual(['old-case'],row['historicalCaseIds']);self.assertEqual([],row['currentWholeCaseRefs']);self.assertTrue(row['currentWholeJoinPending']);self.assertFalse(row['newDispositionCreated'])

    def test_source_or_byte_change_and_prior_ambiguity_never_transfer(self):
        c,o,raw,classes=self.inputs()
        self.assertEqual('SOURCE_CHANGED',bind_one(c,[{**o,'sourceSha256':'b'*64}],raw,classes,classes)[1])
        self.assertEqual('OWNER_PHYSICAL_BYTES_CHANGED',bind_one(c,[o],raw,classes,{'api:p/C.class':'b'*64})[1])
        self.assertEqual('NO_OR_AMBIGUOUS_PRIOR',bind_one(c,[o,o],raw,classes,classes)[1])

    def test_multiple_top_level_types_are_held_without_guessing_owner(self):
        c,o,raw,classes=self.inputs();raw+=b'class Other {}\n';digest=hashlib.sha256(raw).hexdigest();c['sourceSha256']=o['sourceSha256']=digest
        self.assertEqual('OWNER_MAPPING_AMBIGUOUS',bind_one(c,[o],raw,classes,classes)[1])

    def test_missing_empty_whitespace_or_nontext_rationale_never_rebinds(self):
        c,o,raw,classes=self.inputs()
        for value in (None,'','  \n',0,[]):
            row,kind=bind_one(c,[{**o,'reason':value,'priorReason':value}],raw,classes,classes)
            self.assertEqual('MISSING_PRIOR_RATIONALE',kind)
            self.assertEqual('NOT_REVIEWED_CURRENT_SOURCE',row['status'])

    def test_prior_reason_fallback_survives_two_successive_rebinds(self):
        c,o,raw,classes=self.inputs();del o['reason'];o['priorReason']='independent retained reason'
        first,kind=bind_one(c,[o],raw,classes,classes)
        self.assertEqual('REBOUND',kind)
        self.assertEqual('independent retained reason',first['reason'])
        self.assertEqual(first['reason'],first['priorReason'])
        first['status']=first['priorDisposition']
        second,kind=bind_one(c,[first],raw,classes,classes)
        self.assertEqual('REBOUND',kind)
        self.assertEqual(first['reason'],second['reason'])


if __name__=='__main__':unittest.main()
