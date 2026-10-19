import inspect
import unittest
from pyflakes.api import check,checkPath
import pg5576_monitor_whole_public as public
import pg5578_monitor_static as static


class CurrentReaders(unittest.TestCase):
    def test_original_current3905_projection_complete_namespace(self):
        raw=public.main_source();export=public.export_source()
        self.assertIn('pg5574-monitor-whole-qualified-v1',raw);self.assertIn('pg5576-monitor-case-projection-v1',raw)
        self.assertIn('source-full-PG5588',export);self.assertNotIn('PG5550',export)
        self.assertIn('3905',raw);self.assertIn('563',raw);self.assertIn('1664',raw)
        scope=public.namespace();exec(compile(raw,'<new current public reader>','exec'),scope)
        self.assertTrue(callable(scope['main']));self.assertIsNotNone(scope['run'])
        payload='import hashlib,json,re\nfrom pathlib import Path\nimport xml.etree.ElementTree as ET\n'+inspect.getsource(scope['qualify_snapshot'])+inspect.getsource(scope['project_xml'])+export
        self.assertEqual(check(payload,'<current result only>'),0)
        summary=public.counts(inspect.getsource(public.previous.publish_qualification));exec(compile(summary,'<current summary>','exec'),scope)
        self.assertIn('len(trace) != 5',summary);self.assertIn("'newTestIdTrace': 5",summary)
        self.assertTrue(callable(scope['publish_qualification']))

    def test_current_static_producer_exact_names_rules_and_no_old_abi_claim(self):
        data={'source':static.SOURCE,'head':static.SOURCE,'candidateJob':'PG5578-monitor-static-input-v1','staticJob':'PG5578-monitor-static-v1',
            'includeCheckstyle':False,'qualifiedJars':{},'originalStaticManifestSha256':'a'*64,'priorStaticManifestSha256':'b'*64,'sourceSha256':{}}
        raw=static.server_source(data)
        self.assertEqual(check(raw,'<current static producer>'),0)
        self.assertIn('source-full-PG5588',raw);self.assertNotIn('source-full-PG5550',raw)
        self.assertIn('runs/PG5556-snapshot-static-v1/manifest.safe.json',raw)
        self.assertIn('current3905/1664',raw);self.assertIn('F03Accepted=False',raw)
        self.assertIn('actualRuleCountDeltaFromSourceA19',raw)
        with self.assertRaises(ValueError):static.server_source(dict(data,includeCheckstyle=True))
        for path in(public.__file__,static.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
