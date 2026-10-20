"""Overlay cannot change source/rule/coordinates, delete IDs or double-count reviews."""
import unittest
from static_disposition_overlay import apply_decisions,load,BASE,validate_rationales


class ImmutableReviewOverlay(unittest.TestCase):
    def row(self):
        return {'findingId':'one','sourcePath':'src/p/C.java','sourceSha256':'a'*64,'rule':'Rule','beginline':'1','endline':'1','begincolumn':'1','endcolumn':'2','status':'NOT_REVIEWED_CURRENT_SOURCE'}

    def test_exact_delta_preserves_raw_identity_and_input(self):
        row=self.row();decision={**row,'status':'REQUIRED_CONTRACT','reason':'explicit reviewed contract','rawWarningRetained':True}
        result=apply_decisions([row],[decision]);self.assertEqual('REQUIRED_CONTRACT',result[0]['status']);self.assertEqual('NOT_REVIEWED_CURRENT_SOURCE',row['status'])
        for bad in ({**decision,'sourceSha256':'b'*64},{**decision,'begincolumn':'2'},{**decision,'rule':'Other'},{**decision,'findingId':'missing'},{**decision,'status':'PASS'}):
            with self.assertRaises(ValueError):apply_decisions([row],[bad])
        with self.assertRaises(ValueError):apply_decisions([row],[decision,decision])
        with self.assertRaises(ValueError):apply_decisions(result,[decision])

    def test_actual_473_chain_and_foreign_source_rejected(self):
        path=BASE/'PG5772-primary-capture27-v1/manifest.json';digest='b22a70787187534deadba238364e708c3fd749ceb456392795b5e11a81cff487';source='9463db1ac23437043facf95b87f64b9fc7e758bd'
        rows=load(path,digest,source);self.assertEqual(1582,len(rows));self.assertEqual(473,sum(r['status']!='NOT_REVIEWED_CURRENT_SOURCE'for r in rows))
        with self.assertRaisesRegex(ValueError,'one declared source'):load(path,digest,'foreign')

    def test_pending_is_not_final_success_or_executed_pt(self):
        row=self.row();decision={**row,'status':'SOURCE_REBOUND_CURRENT_WHOLE_PENDING','priorDisposition':'REQUIRED_CONTRACT','reason':'individual pending proof','rawWarningRetained':True,'currentWholeJoinPending':True,'currentWholeCaseRefs':[]}
        result=apply_decisions([row],[decision]);self.assertTrue(result[0]['currentWholeJoinPending'])
        for changes in({'currentWholeJoinPending':False},{'currentWholeCaseRefs':[{'testId':'old'}]},{'priorDisposition':'PASS'}):
            with self.assertRaisesRegex(ValueError,'never whole success'):apply_decisions([row],[{**decision,**changes}])
        rows=load(BASE/'PG5788-jms-guard4-v1/manifest.json','bac472e8d9f65dc58725a5ee4d952192dda0a95cb8d910877468ce2547a89ae7','2bbb85a297d7f7bd1b0c243d343e0da509faf99a')
        self.assertEqual(1585,len(rows));self.assertEqual(476,sum(r['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING'for r in rows))

    def test_missing_payload_is_not_a_valid_classification(self):
        for status in ('REQUIRED_CONTRACT','FALSE_POSITIVE','CONTEXT_NOT_APPLICABLE','SOURCE_REBOUND_CURRENT_WHOLE_PENDING'):
            for reason in (None,'',' \n',0):
                with self.assertRaisesRegex(ValueError,'nonblank individual rationale'):
                    validate_rationales([{**self.row(),'status':status,'reason':reason}])
            validate_rationales([{**self.row(),'status':status,'priorReason':'exact independent original reason'}])


if __name__=='__main__':unittest.main()
