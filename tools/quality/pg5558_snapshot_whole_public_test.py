import unittest
from pyflakes.api import check,checkPath
import pg5558_snapshot_whole_public as entry


class PublicOriginal(unittest.TestCase):
    def test_exact_original_current_count_and_namespace(self):
        export=entry.export_source();raw=entry.main_source()
        self.assertIn('source-full-PG5550',export);self.assertNotIn('PG5414',export)
        self.assertIn('3900',export);self.assertIn('563',raw);self.assertIn('1664',raw)
        self.assertIn('pg5552-snapshot-whole-qualified-v1',raw)
        self.assertIn('pg5558-snapshot-case-projection-v1',raw)
        scope={**vars(entry.previous.previous.previous),'SOURCE':entry.SOURCE,'SLOT':entry.SLOT,'export_source':entry.export_source}
        scope.update({'ast':None})
        exec(compile(raw,'<pure projection namespace>','exec'),scope)
        self.assertTrue(callable(scope['main']));self.assertIsNotNone(scope['run'])
        imports='import hashlib,json,re\nfrom pathlib import Path\nimport xml.etree.ElementTree as ET\n'
        self.assertEqual(check(imports+__import__('inspect').getsource(scope['qualify_snapshot'])+__import__('inspect').getsource(scope['project_xml'])+export,'<original projection>'),0)

    def test_public_allowlist_does_not_export_raw_suite_properties(self):
        source=__import__('inspect').getsource(entry.previous.previous.previous.project_xml)
        self.assertIn("'caseNameSha256'",source);self.assertNotIn("'properties'",source)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
