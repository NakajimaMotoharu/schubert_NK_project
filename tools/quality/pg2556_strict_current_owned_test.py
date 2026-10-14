import ast
import json
import unittest
from pg1446_current_cold_stage import W
from pg2554_strict_current_owned_sources import emit, TOOLS, SOURCE
from pg2556_strict_current_owned_dispatch import stage, run_source


class FreshOwnedGraph(unittest.TestCase):
    def test_generated_names_new_source_and_actual_binding_not_historical_authority(self):
        live = json.loads((W / 'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
        # Historical schemas are fixture shapes only, not authority or new
        # terminal observations. Actual sources() refuses until new proofs exist.
        old = json.loads((W / 'pg2452-question-current-terminal-v1/manifest.safe.json').read_bytes())
        projection = json.loads((W / 'pg2472-question-current-parent-projection-v1.safe.json').read_bytes())
        oldseal = json.loads((W / 'pg2456-question-current-full-seal-v1/manifest.safe.json').read_bytes())
        ctx = ('a'*64, oldseal['observedOwned'], oldseal['genuineCompletion'], oldseal['doneEndUtc'])
        values = emit(ctx, live, old['parentState'], projection['parentState18'])
        whole = '\n'.join(values.values())
        for marker in [SOURCE, TOOLS, 'pg2548-strict-current-full-seal-v1',
                       live['binding']['run'], live['binding']['activation'], 'PG2512']:
            self.assertIn(marker, whole)
        for name, raw in values.items():
            if name.endswith('.py'):
                ast.parse(raw)
        self.assertNotIn('pg2458-question-current-owned-stop-tools-v1', whole)

    def test_dispatch_exact_current_stage_frozen_and_single_stop_slots(self):
        raw = run_source(); ast.parse(raw)
        for marker in ['pg2555-frozen-v1.safe.json', 'pg2556-stage-v1.exit',
                       'Pg2554', 'pg2557', 'pg2558']:
            self.assertIn(marker, raw)
        raw = stage()
        self.assertIn('pg2556-' + TOOLS + '.tar', raw)
        self.assertIn('PG2512', raw)
        self.assertNotIn('pg2460-', raw)


if __name__ == '__main__':
    unittest.main()
