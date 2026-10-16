"""No stale-source allowance or premature static success receipt."""
import unittest
from pyflakes.api import check
import pg3970_current_main_static as static


class FixedCurrentMainStatic(unittest.TestCase):
    def test_exact_complete_map_and_missing_changed_extra_refusal(self):
        expected = {str(n): 'a' * 64 for n in range(849)}
        static.verify_maps(expected, dict(expected))
        for candidate in [{**expected, '0': 'b' * 64}, {**expected, 'extra': 'a' * 64}, {k: v for k, v in expected.items() if k != '0'}]:
            with self.assertRaises(ValueError): static.verify_maps(expected, candidate)

    def test_entire_payload_compiles_and_has_no_intermediate_receipt(self):
        source = static.payload({})
        self.assertEqual(0, check(source, '<frozen current849 static>'))
        compile(source, '<frozen current849 static>', 'exec')
        self.assertNotIn("(out/'manifest.safe.json').write_text", static.pmd_source())
        self.assertIn('F03Accepted=False', source)
        self.assertNotIn('rawFindings\'] == 1653', source)


if __name__ == '__main__': unittest.main()
