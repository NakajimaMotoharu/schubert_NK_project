import unittest
from pg2659_operation_candidate_compile import compiler, ARCHIVE, TARGET


class UnusedAbiPreparation(unittest.TestCase):
    def test_exact_new_names_and_current_owned_abi(self):
        raw=compiler()
        for marker in ['pg2659','pg2654','pg2555-frozen-v1','pg2554']:
            self.assertIn(marker,raw)
        self.assertNotIn('pg2459-frozen-v1',raw)
        self.assertTrue(str(TARGET).endswith('pg2658-operation-unused-tools-v1'))
        self.assertTrue(str(ARCHIVE).endswith('pg2660-operation-release-v1.tar'))


if __name__=='__main__':unittest.main()
