import subprocess
import unittest
import pg6722_broker_noop_equivalence as p


class ObserverEquivalenceTest(unittest.TestCase):
    def test_exact_real_two_paths_and_six_old_callsites(self):
        for path,count in p.PATHS.items():
            before=subprocess.check_output(['git','show',p.OLD+':'+path],cwd=p.ROOT,text=True)
            self.assertEqual(count,p.expand_to_original(before,(p.ROOT/path).read_text(),count)['ordinaryCallsites'])

    def test_changed_native_mode_or_literal_not_accepted(self):
        before='class A { void m(){ select(flag, ignored -> {}, 2000); }}'
        after='class A { private static final Consumer<Throwable> ORDINARY_UNCONFIRMED = ignored -> {}; void m(){ select(flag, ORDINARY_UNCONFIRMED, 2000); }}'
        self.assertEqual(1,p.expand_to_original(before,after,1)['sharedDefinitions'])
        for bad in (after.replace('flag,','!flag,'),after.replace('2000','2001')):
            with self.assertRaisesRegex(ValueError,'tokens unchanged'):p.expand_to_original(before,bad,1)

    def test_effectful_observer_duplicate_or_missing_reference_rejected(self):
        before='class A { void m(){ use(ignored -> {}); }}'
        after='class A { private static final Consumer<Throwable> ORDINARY_UNCONFIRMED = ignored -> {}; void m(){ use(ORDINARY_UNCONFIRMED); }}'
        for bad,count in ((after.replace('ignored -> {}','ignored -> { sideEffect(); }'),1),
                          (after.replace('void m()', 'private static final Consumer<Throwable> ORDINARY_UNCONFIRMED = ignored -> {}; void m()'),1),
                          (after,2)):
            with self.assertRaises(ValueError):p.expand_to_original(before,bad,count)


if __name__=='__main__':unittest.main()
