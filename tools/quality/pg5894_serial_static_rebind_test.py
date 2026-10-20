import unittest
import hashlib
import pg5894_serial_static_rebind as target


class FiveChangedOwnersHeldTest(unittest.TestCase):
    def test_no_old_success_or_changed_owner_import(self):
        raw=target.reader_source();self.assertIn('len(used)!=523 or len(held)!=5',raw)
        self.assertIn('currentWholeCaseRefs=[]',raw);self.assertIn('historicalPtImportedAsCurrent=False',raw)
        self.assertIn('PG5860-current3971-cases',raw)

    def test_duplicate_coordinates_need_exact_identity_then_same_source_and_owner(self):
        raw=b'public final class Scope {}\n';digest=hashlib.sha256(raw).hexdigest();row={'findingId':'right','sourcePath':'src/schubert-nk-storage/src/main/java/example/Scope.java','sourceSha256':digest,'rule':'AvoidInstanceofChecksInCatchClause','beginline':'1','endline':'1','begincolumn':'1','endcolumn':'10','diagnosticTextSha256':'a'*64}
        correct={**row,'status':'REQUIRED_CONTRACT','reason':'independent contract'};other={**correct,'findingId':'left'};classes={'storage:example/Scope.class':'b'*64}
        value,kind=target.bind_current(row,[other,correct],raw,classes,classes)
        self.assertEqual('REBOUND',kind);self.assertEqual('right',value['priorFindingId'])
        for altered in({'findingId':'unknown'},{'diagnosticTextSha256':'c'*64},{'endcolumn':'11'},{'sourceSha256':'d'*64}):
            self.assertNotEqual('REBOUND',target.bind_current({**row,**altered},[other,correct],raw,classes,classes)[1])
        self.assertNotEqual('REBOUND',target.bind_current(row,[correct,correct],raw,classes,classes)[1])
        self.assertNotEqual('REBOUND',target.bind_current(row,[],raw,classes,classes)[1])
        self.assertEqual('OWNER_PHYSICAL_BYTES_CHANGED',target.bind_current(row,[other,correct],raw,classes,{k:'e'*64 for k in classes})[1])


if __name__=='__main__':unittest.main()
