import re
import json
import subprocess
import unittest
import pg5264_morning_backup_selected as entry
import pg5265_owned_factory_proof as proof
import pg5266_morning_backup_bytecode as post
import pg5270_scope_classification_morning_backup as classify


class SourcePins(unittest.TestCase):
    def test_all_pins_match_committed_unchanged_production(self):
        self.assertRegex(post.SOURCE,re.compile(r'^[0-9a-f]{40}$'))
        self.assertEqual(post.SOURCE,classify.SOURCE)
        self.assertEqual(subprocess.check_output(['git','rev-parse',post.SOURCE+'^{commit}'],cwd=entry.selected.ROOT,text=True).strip(),post.SOURCE)
        run=entry.selected.ROOT.parent/'pgpt-runs/PG379/pg5264-morning-backup-green-v1/manifest.safe.json'
        self.assertEqual(json.loads(run.read_bytes())['sourceSnapshot'],post.SOURCE)

    def test_invalid_pin_rejected_before_any_run_read(self):
        for value in ('a'*41,'','A'*40,'a'*39):
            with self.assertRaisesRegex(ValueError,'full40hex'):
                proof.prove(entry=None,run_name=None,prior_name=None,source=value,tests=None,suites=None,
                    package=None,scopes=None,kinds=None,out_name=None)


if __name__=='__main__':unittest.main()
