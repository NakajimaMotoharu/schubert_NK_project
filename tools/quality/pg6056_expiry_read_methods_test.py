import unittest
import pg6056_expiry_read_methods as t


class ExactMethodSelectionTest(unittest.TestCase):
    def test_dollar_nested_display_and_all_other_members_unchanged(self):
        read = '  public java.util.Optional<dev.codex.schubert.nk.batch.repository.ExpiryAuditRepository$Snapshot> read(dev.codex.schubert.nk.batch.repository.BatchStepAttempt);'
        helper = '  private static <T> T presentRead(T) throws java.sql.SQLDataException;'
        before = {read: 'old', 'other()': 'same'}
        after = {read: 'fixed', 'other()': 'same', helper: 'new'}
        self.assertEqual(({helper}, {read}), t.intended_change(before, after))
        for broken in (after | {'unexpected()': 'new'}, {read: 'fixed', helper: 'new'},
            after | {'other()': 'changed'}, {k.replace('$Snapshot', '.Snapshot'): v for k, v in after.items()},
            {k.replace('presentRead(T)', 'presentRead(String)'): v for k, v in after.items()}):
            with self.assertRaises(ValueError):
                t.intended_change(before, broken)


if __name__ == '__main__':
    unittest.main()
