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


if __name__=='__main__':unittest.main()
