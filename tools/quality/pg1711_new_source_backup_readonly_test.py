"""Fixed current manifest/byte responsibility and readonly capability closure."""
import ast
import hashlib
import unittest
from pg1711_new_source_backup_readonly import payload
from pg1620_current_backup_config_fixture_oracle import verify_fixture_api


class CurrentBackupTest(unittest.TestCase):
    def test_current_readonly_source_and_independent_fixture(self):
        raw=payload();ast.parse(raw)
        for value in ['pg1711-new-source-backup-readonly-v1','pg1703_parent_receipt.py',
                      '02e941b9-1c52-4018-a193-63dd00b269af','2026-10-12T14:19:28.968927Z',
                      '2741c4546afad6c1e8b6efbd53dfb58144edf7bb','0.1.0-PG1638/config/templates/api.yml']:
            self.assertIn(value,raw)
        for old in ['0be226b1-bbb7-43d3-aa9e-59d0bda70f9a','pg1609_parent_receipt.py',
                    '0.1.0-PG1544/config/templates/api.yml','2026-10-12T06:23:13.176261Z']:
            self.assertNotIn(old,raw)
        self.assertNotIn('StartUnit',raw);self.assertNotIn('StopUnit',raw)
        template=b'api.enabled: true\n# SSC150 default\n"nk.api.storage.asset-manifest-entries": "59627"\napi.version: "1"\n'
        original=b'api.enabled: true\napi.version: "1"\n"nk.api.storage.asset-manifest-entries": "1"\n'
        hashes={'config/templates/api.yml':hashlib.sha256(template).hexdigest()};identity=(0,981,0o640)
        self.assertEqual('SIGNED_TEMPLATE_WITH_ONLY_APPROVED_FIXTURE_ASSET_COUNT_1',
                         verify_fixture_api(original,original,template,identity,identity,981,hashes))
        for bad in [None,b'',original+b'x',original.replace(b'api.enabled: true',b'api.enabled: false'),
                    original.replace(b'"1"\n',b'"2"\n'),original.replace(b'"1"\n',b'null\n')]:
            with self.subTest(input=bad),self.assertRaises(ValueError):
                verify_fixture_api(bad,original,template,identity,identity,981,hashes)


if __name__=='__main__':unittest.main()
