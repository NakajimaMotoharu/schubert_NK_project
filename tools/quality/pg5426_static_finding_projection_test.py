import inspect
import unittest
from pyflakes.api import check,checkPath
import pg5426_static_finding_projection as entry


class StaticProjection(unittest.TestCase):
    def test_ten_individual_source_facts_never_exempt_an_entire_rule(self):
        self.assertEqual(len(entry.REVIEWS),10)
        self.assertEqual(sum(row[0] in ('REQUIRED_CONTRACT','FALSE_POSITIVE') for row in entry.REVIEWS.values()),9)
        self.assertEqual(sum(row[0]=='REVIEW_OPEN_STYLE' for row in entry.REVIEWS.values()),1)
        for (path,rule,line),(_,reason,test,snippet) in entry.REVIEWS.items():
            self.assertTrue(path.endswith('.java'));self.assertTrue(rule);self.assertGreater(line,0)
            self.assertTrue(reason);self.assertTrue(test.endswith('Test'));self.assertTrue(snippet)
        key=('api/idempotency/ResponseSnapshotCodec.java','HardCodedCryptoKey',57)
        self.assertEqual(entry.REVIEWS[key][0],'FALSE_POSITIVE')
        self.assertIn('runtime constructor input',entry.REVIEWS[key][1])

    def test_wrong_source_or_raw_report_is_never_projected_as_zero(self):
        for diagnostic in ({'actualExit':1,'productionSource':entry.SOURCE,'result':{}},
            {'actualExit':0,'productionSource':'foreign','result':{}},
            {'actualExit':0,'productionSource':entry.SOURCE,'result':{'pmd':{'rawFindings':0}}}):
            with self.assertRaises(ValueError):entry.project({},diagnostic,[])
        diagnostic={'actualExit':0,'productionSource':entry.SOURCE,'result':{'pmd':{'rawFindings':1647,'reportSha256':'a'*64}}}
        with self.assertRaises(ValueError):entry.project({'reportSha256':'b'*64,'findings':[]},diagnostic,[])
        raw=inspect.getsource(entry.collect)+'\ncollect()\n'
        self.assertEqual(check(raw,'<readonly metadata only>'),0)
        self.assertNotIn('write_',raw)
        for path in (entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
