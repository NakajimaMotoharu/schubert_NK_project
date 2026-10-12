"""Actual whole generated payload, not unbound fragments or parent-only checks."""
import inspect
import io
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
from pg1588_current_native_catalog_v3 import catalog_source
from pg1590_current_native_qualification_v2 import source
from pg1587_current_native_qualification import CODE,coordinates

class ExactPayloadStaticTest(unittest.TestCase):
    def test_exact_generated_payloads_and_faults(self):
        catalog='SEALS={}\n'+catalog_source()
        server='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="a"\n'+inspect.getsource(coordinates)+'\n'+CODE.replace('PG1587','PG1590')
        for code in [catalog,server]:
            self.assertEqual(check(code,'<actual injected payload>',Reporter(io.StringIO(),io.StringIO())),0)
            self.assertGreater(check('import concurrent.futures\n'+code,'<actual unused import mutation>',Reporter(io.StringIO(),io.StringIO())),0)
        self.assertIn("'pg1588-current-native-catalog-v3/manifest.safe.json'",source())
        self.assertIn("if check(source,",source())

if __name__=='__main__':unittest.main()
