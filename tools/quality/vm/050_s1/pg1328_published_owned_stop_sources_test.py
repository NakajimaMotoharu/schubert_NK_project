import unittest
from pg1328_published_owned_stop_sources import sources,BEFORE,GUEST_BEFORE


class CurrentOwnedStopClosureTest(unittest.TestCase):
    def test_current_genuine_tuple_source_signature_and_fixed_reverse_stop(self):
        files=sources();java=files['Pg1328NativeStop.java']
        for part in ['2026-10-10T23:54:39.918039Z','d2e3a86f-27a4-4c2a-be21-b512eebf1216','841b507c-2713-4ffe-8882-68f5fb3f87f5','0.1.0-PG1292','verifyOriginalValues(epoch,done)']:
            self.assertTrue(part in java,part)
        self.assertTrue('d5b00104280028d9ea81b44c1d1c805f3c2861ed'not in java)
        child=files['pg1328_native_refs.py'];self.assertIn(BEFORE,child);self.assertIn(GUEST_BEFORE,child)
        owned=files['pg1328_native_owned_stop.py']
        for pid in ['811700','809511','808288','715021']:self.assertIn(pid,owned)
        self.assertTrue('672790'not in owned)
        for name,text in files.items():
            if name.endswith('.py'):compile(text,'<actual generated '+name+'>','exec')
        self.assertIn('Pg1328OriginalTupleTest.java',files)


if __name__=='__main__':unittest.main()
