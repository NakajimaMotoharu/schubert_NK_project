"""Actual composed fixed4 seal payload, full static/export closure, no stage replay entry."""
import unittest
from pyflakes.api import check
from pg2056_fixed_seals_runtime_retirement_dispatch import post_payload,run_action


class Fresh(unittest.TestCase):
    def test_actual_fixed_seals_complete_source(self):
        raw=post_payload();self.assertEqual(0,check(raw,'<actual full current fixed4 seal preflight>'))
        self.assertTrue('pg2040-fresh-normal-warning-terminal-post-v1'in raw)
        self.assertTrue('allClientAdvisoryFlock0'in raw)
        with self.assertRaises(ValueError):run_action('stage')


if __name__=='__main__':unittest.main()
