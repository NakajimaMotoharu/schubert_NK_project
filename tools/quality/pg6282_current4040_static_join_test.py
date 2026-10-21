import copy
import hashlib
import unittest
import pg6282_current4040_static_join as subject


class SemanticClassJoin(unittest.TestCase):
    def setUp(self):
        self.source='1'*40;self.text=b'Independent literal semantic Test source\n'
        self.cls='dev.codex.schubert.nk.api.application.QueryTest'
        self.declaration=dict(className=self.cls,sourceSha256=hashlib.sha256(self.text).hexdigest())
        self.case=dict(module='api',testId='PT-INDEPENDENT-001',xmlSha256='2'*64,**{'class':self.cls},
            caseNameSha256='3'*64,source=self.source,result='PASS_ORIGINAL_XML')

    def call(self,declarations=None,cases=None,reader=None):
        return subject.declared_class_references([self.declaration]if declarations is None else declarations,
            [self.case]if cases is None else cases,self.source,(lambda path:self.text)if reader is None else reader)

    def test_exact_source_and_original_xml_fields_not_generated_pass(self):
        paths=[]
        def read(path):paths.append(path);return self.text
        actual=self.call(reader=read)
        self.assertEqual(['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/QueryTest.java'],paths)
        self.assertEqual([dict(testId='PT-INDEPENDENT-001',xmlSha256='2'*64,**{'class':self.cls},caseNameSha256='3'*64,source='1'*40)],actual)

    def test_missing_wrong_source_failed_or_duplicate_cases_rejected(self):
        for change in (lambda c:[],lambda c:[dict(c,source='4'*40)],lambda c:[dict(c,result='FAIL')],lambda c:[c,copy.deepcopy(c)]):
            with self.subTest(change=change),self.assertRaises(ValueError):self.call(cases=change(self.case))

    def test_wrong_source_bytes_and_unsafe_or_duplicate_class_rejected(self):
        with self.assertRaises(ValueError):self.call(reader=lambda path:b'Other source')
        for name in ('../../QueryTest','dev.codex.schubert.nk.other.QueryTest','dev.codex.schubert.nk.api../QueryTest'):
            with self.subTest(name=name),self.assertRaises(ValueError):self.call(declarations=[dict(self.declaration,className=name)])
        with self.assertRaises(ValueError):self.call(declarations=[self.declaration,self.declaration])


if __name__=='__main__':unittest.main()
