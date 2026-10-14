import ast
import json
import unittest
from pg1446_current_cold_stage import W
from pg2516_current_strict_candidate_sources import SOURCE
from pg2544_strict_current_terminal import payload as terminal
from pg2546_strict_current_rows import payload as rows, BEFORE
from pg2548_strict_current_full_seal import payload as seal


class ActualNewGeneration(unittest.TestCase):
    def setUp(self):
        v = json.loads((W / 'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
        self.binding = {**v['binding'], 'rootPid':v['rootPid']}

    def test_whole_terminal_source_actual_binding_and_historical_refusal(self):
        raw = terminal(self.binding, '2f3275b09f26b46932fc3e8eaf269023256e9078027611d617639f43b191395f')
        ast.parse(raw)
        for marker in [SOURCE, self.binding['run'], self.binding['activation'], 'PG2512',
                       'pg2544-strict-current-terminal-v1', 'historical cdbc completion is not new source']:
            self.assertIn(marker, raw)

    def test_actual_all24_oracle_source_before_and_current_paths(self):
        raw = rows(); ast.parse(raw)
        for marker in [BEFORE, self.binding['run'], self.binding['cutoff'], 'pg2540-strict-current-noargs-once-v1',
                       'pg2546-strict-current-rows-v1', 'before=json.loads(br)', 'qualify(before']:
            self.assertIn(marker, raw)
        self.assertNotIn('b89bdd48eecd46af684341c5d0c27f639ce1282a9732086419ca2060bdb2c251', raw)

    def test_whole_seal_exact_current_guard_and_actual_new_before(self):
        raw = seal(self.binding, '2f3275b09f26b46932fc3e8eaf269023256e9078027611d617639f43b191395f')
        ast.parse(raw)
        for marker in [SOURCE, BEFORE, 'pg2548-strict-current-full-seal-v1', 'pg2540-strict-current-noargs-once-v1',
                       'pg2512-manifest.sig', self.binding['run']]:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
