"""Whole stage/runner namespace bindings and immutable historical negative guards."""
import ast
import unittest
import pg3006_current_resume_owned_sources as sources
import pg3010_current_resume_owned_dispatch as dispatch
import pg3012_current_resume_owned_post as post


class CurrentOwned(unittest.TestCase):
    def test_complete_stage_runner_bound_to_new_only_qualified_slots(self):
        for label, raw in [('stage', dispatch.stage()), ('runner', dispatch.run_source())]:
            ast.parse(raw)
            for old in ['pg2890', 'pg2892', 'pg2894', 'pg2902', 'pg2904', 'pg2874', 'pg2878']:
                self.assertFalse(old in raw, (label, old))
        self.assertTrue('pg3008-frozen' in dispatch.run_source())
        self.assertTrue('pg3010-stage-v1.exit' in dispatch.run_source())
        self.assertEqual('pg3000-current-resume-full-seal-v1', dispatch.POST_SLOT)
        self.assertTrue(all(callable(sources.namespace()[n]) for n in ['context', 'emit_receipt', 'emit', 'sources']))
        self.assertTrue(all(callable(post.namespace()[n]) for n in ['emit', 'payload', 'entry']))

    def test_historical_negative_not_rewritten_into_current_run(self):
        raw = "binding.get('run')=='91f5484b-9702-4c7c-97f3-dd5110a853f9'"
        self.assertEqual(raw, sources.bind(raw))
        self.assertEqual("fields[1]=='0dc63b79-3f9a-450c-b2a6-56f86272d272'", sources.bind("fields[1]=='0dc63b79-3f9a-450c-b2a6-56f86272d272'"))


if __name__ == '__main__':
    unittest.main()
