"""Closed Test-only server namespaces and explicit same3691 fixture/byte oracles."""
import unittest
import pg3200_expiry_boundary_selected as tool


class ExpirySelected(unittest.TestCase):
    def test_both_whole_suites_have_new_literal_test_methods_and_fixed_main(self):
        for choice, (label, _, test, subject, methods) in tool.CHOICES.items():
            raw = tool.server(choice)
            for token in [label, 'source-full-PG3054', 'repository.' + test, '/' + subject + "'", 'baseFixturesUnchanged', 'mainRecompiled', 'targetCounters'] + methods:
                self.assertTrue(token in raw, token)
            for historical in ['source-full-PG3026', 'platform.ExpiryWorkerRequestTest', 'ereq3042001']:
                self.assertFalse(historical in raw, historical)
        self.assertEqual(5, len(tool.FILES))
        self.assertTrue(all('/src/test/' in n or n.startswith('tools/') for n in tool.FILES))


if __name__ == '__main__':
    unittest.main()
