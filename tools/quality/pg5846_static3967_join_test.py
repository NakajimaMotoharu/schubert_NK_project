import unittest
from pg5846_static3967_join import reader_source,validate_cases


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


if __name__=='__main__':unittest.main()
