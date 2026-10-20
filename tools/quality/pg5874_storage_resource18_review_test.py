import unittest
from pg5874_storage_resource18_review import ROOT,PATH,verify_shape,EXPECTED


class ScopeReviewCountercheck(unittest.TestCase):
    def test_both_families_and_negative_priority_or_normalization_mutations(self):
        text=(ROOT/PATH).read_text();verify_shape(text)
        self.assertEqual(18,sum(EXPECTED.values()))
        for bad in(text.replace('throw secondary;','throw primary;',1),text.replace('throw primary;','return null;',1),text.replace('primary.addSuppressed(new StorageIoException(StorageIoException.Reason.UNAVAILABLE));','primary.addSuppressed(secondary);',1),text.replace('if (resource != null) {','if (resource == null) {',1),text.replace('failure.getSuppressed().length == 0','failure.getSuppressed().length >= 0',1)):
            with self.assertRaises(ValueError):verify_shape(bad)


if __name__=='__main__':unittest.main()
