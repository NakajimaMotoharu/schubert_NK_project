import unittest
from pg5820_identity14_review import guarded_identity,prior_reason


class ExactGuardControlTest(unittest.TestCase):
    def test_legacy_reason_retained_but_missing_basis_is_not_success(self):
        self.assertEqual('reason',prior_reason({'reason':'reason'}))
        self.assertEqual('inherited',prior_reason({'priorReason':'inherited'}))
        for row in({}, {'reason':[]},{'priorReason':' '}):
            with self.assertRaises(ValueError):prior_reason(row)

    def test_only_same_typed_pair_without_intervening_effects(self):
        f={'leftExpression':'a','rightExpression':'b','operator':'NOT_EQUAL_TO','firstLine':'1','lastLine':'1','firstColumn':'5','lastColumn':'10'}
        self.assertEqual('DISTINCT_THROWABLE_APPEND',guarded_identity('if (a != b) { a.addSuppressed(b); }',f))
        for text in('if (a != b) { a.addSuppressed(a); }','if (a != b) { mutate(); a.addSuppressed(b); }','if (a == b) { a.addSuppressed(b); }'):
            with self.assertRaises(ValueError):guarded_identity(text,f)
        self.assertEqual('IDENTICAL_THROWABLE_EARLY_RETURN',guarded_identity('if (a == b) return; a.addSuppressed(b);',{**f,'operator':'EQUAL_TO'}))
        for last in('9','11'):
            with self.assertRaises(ValueError):guarded_identity('if (a != b) { a.addSuppressed(b); }',{**f,'lastColumn':last})


if __name__=='__main__':unittest.main()
