"""Independent literals: prior fields unchanged, sole native augmentation, full delta retained."""
import unittest
from unittest.mock import patch
import pg2062_native_augmented_retirement_post as p
from pg2040_fresh_normal_warning_terminal_post import SEALS


class Schema(unittest.TestCase):
    def test_exact_augmentation_and_negatives(self):
        prior={'rows':[7],'runtime':{'directory':'original'}}
        before={**prior,'native':{'one':{'sha':'independent'}}};after=dict(before)
        self.assertTrue(p.prior_equal(prior,before,after))
        for bad in [None,{},dict(before,rows=[8]),dict(before,extra=7),dict(before,native=None),dict(before,native={})]:
            self.assertFalse(p.prior_equal(prior,bad,after))
        self.assertFalse(p.prior_equal(prior,before,dict(after,native={'foreign':1})))
        self.assertFalse(p.prior_equal(dict(prior,native={}),before,after))

    def test_actual_full_post(self):
        raw=p.payload({n:'a'*64 for n in SEALS})
        for marker in ['same_except_runtime','prior_equal(json.loads(prior_raw),before,after)','all24UnchangedTwice','allClientAdvisoryFlock0','exactRuntimeEntryRetired']:
            self.assertTrue(marker in raw,marker)

    def test_real_entry_binding_without_recursive_factory(self):
        def actual_entry():
            raw=p.previous.payload({n:'a'*64 for n in SEALS})
            self.assertTrue(p.SLOT in raw)
            return 0
        with patch.object(p.previous,'main',actual_entry),patch.object(p.previous,'payload'),patch.object(p.previous,'SLOT',p.original_slot):
            self.assertEqual(0,p.main())


if __name__=='__main__':unittest.main()
