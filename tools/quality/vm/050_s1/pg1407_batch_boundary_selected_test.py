"""Independent old/fresh/missing/foreign XML and full actual reactor scope contracts."""
import os
from pathlib import Path
import tempfile
import unittest
import pg1407_batch_boundary_selected_v2 as p

class Test(unittest.TestCase):
    def test_fresh_xml_contract(self):
        with tempfile.TemporaryDirectory(dir='/dev/shm')as d:
            path=Path(d)/'report.xml';self.assertIsNone(p.fresh_xml(path,'gold',100))
            path.write_text('<testsuite name="gold" tests="20" failures="0" errors="0" skipped="0"/>')
            os.utime(path,ns=(99,99));self.assertIsNone(p.fresh_xml(path,'gold',100))
            os.utime(path,ns=(100,100));self.assertEqual({'tests':20,'failures':0,'errors':0,'skipped':0},p.fresh_xml(path,'gold',100))
            self.assertIsNone(p.fresh_xml(path,'foreign',100))
            link=Path(d)/'alias';link.symlink_to(path);self.assertIsNone(p.fresh_xml(link,'gold',100))
    def test_whole_scope_and_prior_preservation(self):
        raw=p.source()
        for s in ("'-pl','src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap','-DskipTests'", "'src/schubert-nk-batch'",'len(dependency_same)==3',"stale-original-",'freshXmlRequired',"'notRunCount'",'allBatchMainClassBytesEqual1279'):
            self.assertIn(s,raw)
        self.assertNotIn("'src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-batch'",raw)
        compile(raw,'<whole corrected scope>','exec')

if __name__=='__main__':unittest.main()
