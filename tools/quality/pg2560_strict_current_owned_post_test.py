import ast
import json
import unittest
import pg1257_fresh_independent_terminal_post as schema
from pg2560_strict_current_owned_post import emit
from pg1446_current_cold_stage import W
from pg2516_current_strict_candidate_sources import SOURCE


class WholeStopped(unittest.TestCase):
    def test_complete_fresh_source_before_receipt_and_stop_names(self):
        live = json.loads((W / 'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
        # Fixture schemas, not acceptance of old identities or old stop state.
        old = json.loads((W / 'pg2456-question-current-full-seal-v1/manifest.safe.json').read_bytes())
        ctx = ('a'*64, old['observedOwned'], old['genuineCompletion'], old['doneEndUtc'])
        raw = emit({n:'a'*64 for n in schema.previous.SEALS}, ctx, live)
        ast.parse(raw)
        for marker in [SOURCE, 'PG2512', 'pg2554-strict-current-owned-stop-tools-v1',
                       'pg2548-strict-current-full-seal-v1', 'pg2560-strict-current-owned-post-v1',
                       'allTenUnitsKernelEmpty', 'allClientAdvisoryFlock0', 'receipt = ast.parse(RECEIPT)',
                       "summary = e['completed'](receipt_rows"]:
            self.assertIn(marker, raw)
        self.assertNotIn('pg2458-question-current-owned-stop-tools-v1', raw)

    def test_missing_seals_refused_before_guest_operation(self):
        live = json.loads((W / 'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
        with self.assertRaises(ValueError):
            emit({}, ('a'*64, {}, {}, None), live)


if __name__ == '__main__':
    unittest.main()
