"""Public whitelist/actual module slots, independent fixture, refused failure."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pg1804_warning_recovery_public as actual


class Public(unittest.TestCase):
    def exercise(self,code):
        with tempfile.TemporaryDirectory(prefix='pg1804-fixture-')as tmp:
            root=Path(tmp);target=root/'evidence/01_PT/018_NK-OPS-001/evidence/output';target.mkdir(parents=True)
            for slot in [actual.RECOVERY_SLOT,actual.POST_SLOT]:
                directory=root/slot;directory.mkdir()
                (directory/'manifest.safe.json').write_text(json.dumps({'actualExit':code,'guest':{'actualExit':code,'recoveredPairAbsent':True,'password':'FIXTURE_MUST_NOT_EXPORT','sessionId':'FIXTURE_MUST_NOT_EXPORT'},'payloadSha256':'a'*64}))
            with patch.object(actual,'W',root),patch.object(actual,'ROOT',root),patch.object(actual.subprocess,'check_output',return_value='8c37abcee33b392a73e91ff20379fa64b35add0f'),contextlib.redirect_stdout(io.StringIO()):actual.main()
            result=json.loads((target/'695_manifest.json').read_bytes())
            self.assertFalse('FIXTURE_MUST_NOT_EXPORT'in json.dumps(result));self.assertEqual(2,len(result['observations']));self.assertFalse(result['formalAccepted'])
            self.assertEqual([actual.RECOVERY_SLOT,actual.POST_SLOT],[v['slot']for v in result['observations']])

    def test_whitelist_real_slot_and_hashes(self):self.exercise(0)
    def test_failure_not_published(self):
        with self.assertRaises(ValueError):self.exercise(1)


if __name__=='__main__':unittest.main()
