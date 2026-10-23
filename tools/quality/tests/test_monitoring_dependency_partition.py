"""Metadata-only compatibility/negative checks; no Java, target initializer or external file use."""
import unittest
from pg7008_monitoring_mode_post import partitioned_auxiliary_jars

class DependencyPartitionTest(unittest.TestCase):
    def test_empty_production_preserves_old_sdk_identity_without_mutation(self):
        sdk={'/owned/sdk.jar':'1'*64};before=dict(sdk)
        self.assertEqual(sdk,partitioned_auxiliary_jars(sdk,{}))
        self.assertEqual(before,sdk)

    def test_exact_separate_libraries_merge_only_for_classpath(self):
        sdk={'/owned/sdk.jar':'1'*64};production={'/owned/protocol.jar':'2'*64}
        self.assertEqual({**sdk,**production},partitioned_auxiliary_jars(sdk,production))
        self.assertEqual({'/owned/sdk.jar':'1'*64},sdk)
        self.assertEqual({'/owned/protocol.jar':'2'*64},production)
        self.assertEqual(production,partitioned_auxiliary_jars({},production))

    def test_overlapping_roles_rejected_even_with_identical_hash(self):
        for digest in ('1'*64,'2'*64):
            with self.assertRaises(ValueError):partitioned_auxiliary_jars({'/owned/a.jar':'1'*64},{'/owned/a.jar':digest})

    def test_unknown_relative_and_malformed_pins_rejected(self):
        for sdk,production in ((None,{}),({},None),([],{}),({'relative.jar':'1'*64},{}),
          ({'/owned/a.jar':None},{}),({}, {'/owned/b.jar':'g'*64}),({}, {'/owned/b.jar':'A'*64}),
          ({'/owned/a.jar':'1'*63},{})):
            with self.assertRaises(ValueError):partitioned_auxiliary_jars(sdk,production)

if __name__=='__main__':unittest.main()
