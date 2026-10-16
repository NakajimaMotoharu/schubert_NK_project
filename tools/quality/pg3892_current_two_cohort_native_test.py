"""Independent source/cache/count boundaries, no actual VM native reads or merging."""
import ast
import unittest
from unittest.mock import patch
import pg3892_current_two_cohort_native as tool
import pg3890_current_resume_native_catalog as catalog
from pg3832_hygiene_native_qualified import qualify_snapshot


class CurrentCohorts(unittest.TestCase):
    def test_genuine_host_and_exact_two_current_cache_roles(self):
        qualify_snapshot()
        raw=tool.source();ast.parse(raw);server=tool.server();ast.parse(server)
        for text in ['pg3832-hygiene-native-qualified-v1','pg3830-hygiene-native-catalog-v1','pg3890-current-resume-native-catalog-v1','pg3738-hygiene-whole-qualified-v1','same-current immutable cache mismatch','len(old_input[\'selected\'])==10']:
            self.assertIn(text,raw)
        self.assertNotIn('pg3532-outbox',raw);self.assertNotIn('PG3632',raw+server)
        for text in [tool.SOURCE,'PG3734',"len(v['selected'])==20",'require(len(streams)==18)',"'historicalSourceNativeImported':False"]:self.assertIn(text,server)
        self.assertNotIn('3712',server)

    def test_current_resume_admission_keeps_all40_before_copies(self):
        receipt='def completed(*args):raise ValueError("fixture classifier never executed")\n'
        with patch.object(catalog,'current'):
            binding=catalog.root.live()['binding']
            raw=catalog.catalog_source(receipt,binding,binding['start']+1000)
        ast.parse(raw);self.assertTrue(raw.startswith(receipt+'\n'))
        for text in [catalog.SOURCE,catalog.BOM,catalog.ONCE,catalog.root.before(),'==40','all40BeforeCopiesPreserved',"issued['freshCompletedRunResume']is True", "issued['selectedRun']=="+repr(catalog.RUN)]:self.assertIn(text,raw)
        self.assertNotIn("issued['ordinaryNoargs']",raw)


if __name__=='__main__':unittest.main()
