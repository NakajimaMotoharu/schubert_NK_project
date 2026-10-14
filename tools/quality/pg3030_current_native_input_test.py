"""Whole native/server transport export and strict actual3685/not old3684 contract."""
import inspect
import unittest
from pyflakes.api import check
import pg3030_current_resume_native_qualified as native


class CurrentInput(unittest.TestCase):
    def test_complete_new_native_transport_and_member_server(self):
        raw = native.source()
        for token in ['pg3022-current-resume-native-catalog-v1', 'pg3028-extra-row-full-qualified-v1', 'pg3030-current-resume-native-qualified-v1', "data['nativeQualifiedFull']=old_native['qualifiedFull']"]:
            self.assertTrue(token in raw, token)
        for old in ['pg2906-network', 'PG3030-native-v2', 'PG3030-native-input-v2.tar']:
            self.assertFalse(old in raw, old)
        code = native.server()
        extractor = native.transport.prior.previous.entry().__globals__['coordinates']
        prefix = 'import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="a"\n'
        self.assertEqual(0, check(prefix + inspect.getsource(extractor) + '\n' + code, '<complete new native server>'))
        self.assertTrue('source-full-PG3026' in code)
        self.assertTrue('identical_main==1643' in code)
        self.assertTrue('len(streams)==9' in code)
        self.assertTrue('3685' in code)


if __name__ == '__main__':
    unittest.main()
