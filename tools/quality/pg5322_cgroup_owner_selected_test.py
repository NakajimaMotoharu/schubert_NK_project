import re
import unittest
import pg5322_cgroup_owner_selected as role

NAMES=('cgroupfd001SixPrimitiveHighDescriptorsKeepOriginalForwardCloseOrder',
    'cgroupfd002NullCapacityClosedAndForeignParentFailBeforeNativeIo',
    'cgroupfd003NegativeAndDuplicateNeverOwnAnExtraFdButZeroIsValid',
    'cgroupfd004AllOpenFailuresReleaseOnlyPreviouslyOwnedDescriptors',
    'cgroupfd005All64ForwardCloseStatesMatchLiteralIndependentGolden',
    'cgroupfd006ExistingAndRepeatedSuppressionKeepIdentityAndSanitizeLaterFailures',
    'cgroupfd007SixSlotsDrainEveryLaterFdBeforeUnknownAggregationAndNeverRetry',
    'cgroupfd008ParallelOwnersNeverShareSlotsOrConsumeEachOther')


class CgroupOwnerScope(unittest.TestCase):
    def test_exact_new_eight_and_existing_ten_cases(self):
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        actual={}
        for name in role.RELATED:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(methods),raw.count('@Test'))
            actual[name.rpartition('.')[2]]=len(methods)
            if name.endswith('.CgroupPrimitiveOwnerTest'):
                self.assertEqual(tuple(methods),NAMES)
                for literal in ('NIREIIRERRRREEEE','0000000001110111','xx22xx2211111111'):
                    self.assertIn('"'+literal+'"',raw)
        self.assertEqual(actual,{'CgroupPrimitiveOwnerTest':8,'MaintenanceUnitTerminationTest':10})
        self.assertFalse(set(role.RELATED)&set(role.previous.extra_suites()))

    def test_bounded_native_owner_families_and_repeat_contract(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),55)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),169)
        self.assertEqual(len(role.extra_suites()),100)
        self.assertEqual(role.repetitions(),role.previous.repetitions())


if __name__=='__main__':unittest.main()
