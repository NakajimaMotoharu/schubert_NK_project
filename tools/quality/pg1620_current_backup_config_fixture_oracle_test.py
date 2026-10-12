"""Signed default vs explicit fixture literal, mutation and ownership vectors."""
import hashlib
import unittest
from pg1620_current_backup_config_fixture_oracle import verify_fixture_api
from pg1621_current_ordinary_backup_qualification_v2 import payload

class FixtureBackupApiTest(unittest.TestCase):
    def test_exact_approved_override_only_not_host_generated_expected(self):
        template=b'api.enabled: true\n# SSC150 default\n"nk.api.storage.asset-manifest-entries": "59627"\napi.version: "1"\n'
        host=b'api.enabled: true\napi.version: "1"\n"nk.api.storage.asset-manifest-entries": "1"\n'
        hashes={'config/templates/api.yml':hashlib.sha256(template).hexdigest()};identity=(0,981,0o640)
        self.assertEqual(verify_fixture_api(host,host,template,identity,identity,981,hashes),'SIGNED_TEMPLATE_WITH_ONLY_APPROVED_FIXTURE_ASSET_COUNT_1')
        for changed in [host.replace(b'"1"',b'"2"'),host.replace(b'"1"\n',b'"01"\n'),host.replace(b'api.enabled: true',b'api.enabled: false'),host+host.splitlines()[-1]+b'\n',host.replace(b'"1"\n',b'"1\n'),host.replace(b'"1"\n',b'null\n'),b'']:
            with self.assertRaises(ValueError):verify_fixture_api(changed,changed,template,identity,identity,981,hashes)
        for archive,body,tpl,source_id,archive_id,gid,signed in [(None,host,template,identity,identity,981,hashes),(host+b'x',host,template,identity,identity,981,hashes),(host,host,template+b'\n',identity,identity,981,hashes),(host,host,template,(0,981,0o600),identity,981,hashes),(host,host,template,identity,identity,982,hashes),(host,host,template,identity,identity,981,{})]:
            with self.assertRaises(ValueError):verify_fixture_api(archive,body,tpl,source_id,archive_id,gid,signed)
        raw=payload();self.assertIn('pg1621-current-ordinary-backup-qualified-v2',raw);self.assertIn("if m.name=='api.yml':",raw)
        self.assertIn('config_oracle.verify_member(m.name',raw);self.assertIn('FIXTURE_SOURCE=',raw)
        self.assertIn("retiredOlderGenerationPrivateBytesQualificationPending':True",raw)

if __name__=='__main__':unittest.main()
