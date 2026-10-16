"""Independent final retire-only dispatcher and exact all11/post contracts, no VM actions."""
import ast
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check
from immutable_payload_binding import PROTECTED
from pg1446_current_cold_stage import W
import pg3902_current_runtime_retirement_sources as role
import pg3906_current_runtime_retirement_dispatch as dispatch
import pg3908_current_runtime_retirement_post as post
import pg1257_fresh_independent_terminal_post as schema


class CurrentRetirement(unittest.TestCase):
    def test_final_retire_only_admission_and_original_stop_prequal(self):
        raw=dispatch.run_source();ast.parse(raw)
        for text in ["('stage', 'retire')",'Pg3902NativeStop retire','pg3906-stage-v1.exit','pg3904-frozen-v1.safe.json']:self.assertIn(text,raw)
        self.assertNotIn('Pg3902NativeStop stop',raw)
        self.assertIn(dispatch.ARCHIVE,dispatch.STAGE);self.assertIn(dispatch.REMOTE,dispatch.STAGE)
        self.assertEqual(role.SHA,dispatch.context()[0]);self.assertEqual(0,check(dispatch.post_payload(),'<genuine current original stopped prequal>'))

    def test_full_independent_literal_and_no_raw_embedded_snapshot_translation(self):
        proof=json.loads((W/'pg3882-current-resume-owned-post-v1/manifest.safe.json').read_bytes())
        seals={n:proof['proofHashes'][n]['sha256']for n in schema.previous.SEALS}
        original=post.stopped.payload(seals)
        protected=[n for n in ast.walk(ast.parse(original))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in n.targets)]
        self.assertEqual([],protected) # Data/parent receipt is injected AFTER role translation.
        raw=post.payload(seals);ast.parse(raw)
        for text in ['same_except_runtime','prior_equal(json.loads(prior_raw),before,after)','zz-pg3844-once-resume.conf','exactRuntimeEntryRetired','pg3902-native-stop-v1']:self.assertIn(text,raw)
        for old in ['pg2392','pg2374','pg3034','zz-pg3564']:self.assertNotIn(old,raw)
        with patch.object(post.stopped,'payload',return_value="ORACLE='untrusted history pg3876'\n"):
            with self.assertRaises(ValueError):post.payload(seals)


if __name__=='__main__':unittest.main()
