import unittest
import hashlib
from pg5846_static3967_join import reader_source,validate_cases,qualification_source,current_reference


class Current482OriginalCaseJoinTest(unittest.TestCase):
    def test_pending_counts_keep_all_raw_and_static_only_contracts(self):
        raw=reader_source()
        for text in('joined!=482','static_only!=239','len(result)!=1594','PG5808-current3955-cases','PG5842-identity13-v1','currentWholeJoinPending=False'):
            self.assertIn(text,raw)
        self.assertNotIn('Popen',raw);self.assertNotIn('subprocess.run',raw)

    def test_case_schema_has_xml_provenance_not_invented_source_field(self):
        cases=[{'testId':str(i),'result':'PASS_ORIGINAL_XML','module':'protocol','sourceXml':'fixed.xml','xmlSha256':'a'*64}for i in range(3967)]
        q={'modules':{'protocol':{'xmlHashes':{'fixed.xml':'a'*64}}}}
        validate_cases(cases,q)
        for change in({'xmlSha256':'b'*64},{'result':'UNKNOWN'},{'testId':'1'}):
            broken=[{**cases[0],**change},*cases[1:]]
            with self.assertRaises(ValueError):validate_cases(broken,q)

    def test_nested_generated_namespace_contains_its_own_helper(self):
        namespace={};exec(compile(qualification_source(),'<independent nested reader namespace>','exec'),namespace)
        self.assertIs(namespace['qualified_whole'].__globals__['validate_cases'],namespace['validate_cases'])
        self.assertIsNot(namespace['validate_cases'],validate_cases)
        with self.assertRaises(ValueError):namespace['validate_cases']([],{'modules':{}})

    def test_selected_method_reference_requires_one_actual_full_xml(self):
        h={'class':'dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationExceptionTest','method':'iso009PrimaryAndProtocolAreRequired','designTestId':'PT-JMS-ISO009'}
        plain=hashlib.sha256(h['method'].encode()).hexdigest();suffix=hashlib.sha256((h['method']+'()').encode()).hexdigest()
        case={'testId':'current','class':h['class'],'xmlSha256':'a'*64,'caseNameSha256':plain,'result':'PASS_ORIGINAL_XML'}
        self.assertEqual('current',current_reference(h,{(h['class'],plain):[case]})['testId'])
        self.assertEqual('current',current_reference(h,{(h['class'],suffix):[{**case,'caseNameSha256':suffix}]})['testId'])
        for index in({}, {(h['class'],plain):[case,case]}, {(h['class'],plain):[{**case,'result':'UNKNOWN'}]}, {(h['class'],plain):[case],(h['class'],suffix):[case]}):
            with self.assertRaises(ValueError):current_reference(h,index)
        for bad in({**h,'designTestId':'PT-JMS-ISO999'},{**h,'class':'other'},{**h,'caseNameSha256':plain}):
            with self.assertRaises(ValueError):current_reference(bad,{(h['class'],plain):[case]})


if __name__=='__main__':unittest.main()
