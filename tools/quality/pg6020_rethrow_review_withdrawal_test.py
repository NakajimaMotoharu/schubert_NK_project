import unittest
import hashlib
from pg6020_rethrow_review_withdrawal import refine,same_raw_identity,IDENTITY,is_error_diagnostic


class PerAlternativeJdkCatchHierarchyTest(unittest.TestCase):
    def pair(self,caught,following):
        one=dict(path='C.java',tryStart='0',catchTotal='2',catchIndex='0',pureSingleRethrow='true',exactUncheckedRoots='true',type=caught,method='C#test()',residualTryStable='true',laterCatchOverlap='true'if following=='java.lang.Throwable'or 'java.lang.RuntimeException'in caught else'false')
        two={**one,'catchIndex':'1','type':following,'pureSingleRethrow':'false','exactUncheckedRoots':'false'}
        return one,two

    def test_exception_keeps_runtime_only_and_throwable_keeps_both(self):
        actions,protected=refine(self.pair('java.lang.RuntimeException|java.lang.Error','java.lang.Exception'))
        self.assertEqual(['java.lang.RuntimeException'],actions[0]['keptTypes']);self.assertEqual(['java.lang.Error'],actions[0]['removedTypes']);self.assertEqual([],protected)
        actions,protected=refine(self.pair('java.lang.RuntimeException|java.lang.Error','java.lang.Throwable'))
        self.assertEqual([],actions);self.assertEqual(['java.lang.RuntimeException','java.lang.Error'],protected[0]['keptTypes'])

    def test_error_is_not_exception_and_coarse_mismatch_or_missing_sibling_is_rejected(self):
        rows=self.pair('java.lang.Error','java.lang.Exception');actions,_=refine(rows);self.assertEqual('REMOVE_PURE_CATCH',actions[0]['kind'])
        with self.assertRaises(ValueError):refine([{**rows[0],'laterCatchOverlap':'true'},rows[1]])
        with self.assertRaises(ValueError):refine([rows[0]])

    def test_review_status_changes_but_no_raw_identity_or_order_may_change(self):
        raw=[{**{k:'fixture'for k in IDENTITY},'findingId':str(i),'status':'NOT_REVIEWED_CURRENT_SOURCE'}for i in range(2)]
        rows=[{**r,'status':'SOURCE_REBOUND_CURRENT_WHOLE_PENDING'}for r in raw];same_raw_identity(raw,rows)
        for key in ('sourceSha256','beginline','rawXmlOrdinal','diagnosticTextSha256'):
            with self.assertRaises(ValueError):same_raw_identity(raw,[{**rows[0],key:'wrong'},rows[1]])
        for bad in ([*reversed(raw)],[raw[0],raw[0]],[{**raw[0],'unknown':'field'},raw[1]],[{**raw[0],'status':'PASS'},raw[1]]):
            with self.assertRaises(ValueError):same_raw_identity(bad,rows)

    def test_reported_error_span_whitespace_and_diagnostic_text_are_both_checked(self):
        source='  catch (RuntimeException | Error failure) {\n'
        start=source.index('Error')+1
        row=dict(beginline='1',endline='1',begincolumn=str(start),endcolumn=str(start+5),diagnosticTextSha256=hashlib.sha256(b'Avoid catching Error in try-catch block').hexdigest())
        self.assertTrue(is_error_diagnostic(source,row))
        self.assertFalse(is_error_diagnostic(source,{**row,'diagnosticTextSha256':'wrong'}))
        self.assertFalse(is_error_diagnostic(source,{**row,'begincolumn':'10','endcolumn':'26'}))


if __name__=='__main__':unittest.main()
