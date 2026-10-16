import ast
import copy
import unittest
import pg4348_current_partial_recover as subject


class CurrentEntry(unittest.TestCase):
    def receipt(self, code):
        return {'actualExit': code, 'source': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
                'payloadSha256': '87ef52f80156a0c83ae1451a08f1b20508797c6072c9b86263af90b163569182',
                'oldParentNormal': False, 'formalAccepted': False}

    def test_nonzero_actual_transport_preserved_without143_assumption(self):
        for code in [1, 143, 255]:
            value = self.receipt(code)
            self.assertIs(value, subject.original_receipt(value))
        for code in [0, False, True, None, '255', -1, 256]:
            with self.subTest(code=code), self.assertRaises(ValueError):
                subject.original_receipt(self.receipt(code))

    def test_all_missing_or_foreign_binding_rejected(self):
        for key in self.receipt(255):
            value = copy.deepcopy(self.receipt(255))
            del value[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                subject.original_receipt(value)
        for key in ['source', 'payloadSha256', 'oldParentNormal', 'formalAccepted']:
            value = self.receipt(255)
            value[key] = 'foreign'
            with self.assertRaises(ValueError):
                subject.original_receipt(value)

    def test_full_entry_keeps_post_true_scope_and_natural_gate(self):
        raw = subject.main_source()
        ast.parse(raw)
        for expected in ["frame('SSC292_PAIR_READY '", 'acquired.wait(30)', "job('partial.py','inspect'", "job('partial.py','recover'", "job('post.py',None", "newMARDDBTenRefNormalClose", "receipt['actualExit']", 'newTenRefsNormalClose']:
            self.assertIn(expected, raw)
        self.assertNotIn("'old4152Exit':143", raw)


if __name__ == '__main__':
    unittest.main()
