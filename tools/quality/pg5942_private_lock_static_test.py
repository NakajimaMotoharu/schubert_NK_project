import unittest
from unittest.mock import patch
import pg5940_private_lock_compile as c
import pg5942_private_lock_static as t


class DeclaredPrivateLocksAuditTest(unittest.TestCase):
    def test_required_target_and_all_other_owner_byte_invariance(self):
        old = {str(i)+'.class': 'before' for i in range(1666)}; old['api:A.class'] = old.pop('0.class')
        declaration = {'requiredClassKeys': ['api:A.class'], 'sourcePlans': [{'module': 'api', 'path': 'src/schubert-nk-api/src/main/java/A.java'}]}
        new = dict(old); new['api:A.class'] = 'after'
        with patch.object(c, 'plan', return_value=declaration):
            self.assertEqual(['api:A.class'], c.physical_changes(old, new))
            for bad in (old, {**new, '1.class': 'wrong'}, {k:v for k,v in new.items() if k!='1.class'}, {**new, 'extra.class':'bad'}):
                with self.assertRaises(ValueError):
                    c.physical_changes(old, bad)

    def test_raw_exact93_and_unrelated_diagnostics_not_suppressed(self):
        t.expected_rules({'AvoidSynchronizedStatement': 154, 'Other': 10}, {'AvoidSynchronizedStatement': 61, 'Other': 10})
        for bad in ({'AvoidSynchronizedStatement': 60, 'Other': 10}, {'AvoidSynchronizedStatement': 61, 'Other': 9}, {'AvoidSynchronizedStatement': 61, 'Other': 10, 'Added': 1}):
            with self.assertRaises(ValueError):
                t.expected_rules({'AvoidSynchronizedStatement': 154, 'Other': 10}, bad)


if __name__ == '__main__':
    unittest.main()
