import unittest
from pg2550_strict_current_a01 import code
import pg2470_question_current_a01_test as previous_oracle


class FreshA01(unittest.TestCase):
    def test_exact_current_root_source_before_budget_and_unchanged_driver(self):
        raw = code()
        for literal in ['a79b45b5858a186fa82bec1ff36882271ab996a4',
                        '2f3275b09f26b46932fc3e8eaf269023256e9078027611d617639f43b191395f',
                        "issued['MainPID']=='287080'", "m['InvocationID']=='bab15677a060455482b670f6ae1dbd0b'",
                        'pg2538-parent-watch-v1.private.jsonl', 'pg2540-strict-current-noargs-once-v1',
                        'pg2536-strict-normal-publication-post-v1/manifest.safe.json', '1800000000',
                        'NativeNkA01Capture', '122dcc4c1be482ac3239325de6fb3d4bec12747d05adce3929c319ab5bdfd71d']:
            self.assertIn(literal, raw)
        self.assertNotIn('systemctl start', raw)
        self.assertNotIn('daemon-reload', raw)
        self.assertNotIn("issued['MainPID']=='194154'", raw)

    def test_fixed_current_baseline_dif_and_secret_negative_oracle(self):
        previous_oracle.ActualA01().test_independent_fixed_current_dif_only_and_secret_negatives()


if __name__ == '__main__':
    unittest.main()
