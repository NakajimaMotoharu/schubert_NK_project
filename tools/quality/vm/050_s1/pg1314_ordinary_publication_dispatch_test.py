"""Compile complete sent payload and verify one-shot reservation precedes SSH actions."""
import unittest
from pg1314_ordinary_publication_dispatch import source,STAGE,GUEST


class PublicationDispatchTest(unittest.TestCase):
    def test_complete_payload_namespace_and_reservation(self):
        code=source();compile(code,'<actual dispatch>','exec');compile(STAGE,'<actual stage>','exec')
        self.assertIn('pg1311-native-tools-v1',GUEST)
        self.assertIn('pg1312-frozen-v1.safe.json',code)
        self.assertIn('pg1313-current-readonly-v1.safe.json',code)
        self.assertIn('Pg1311OrdinaryPublication activate',code)
        self.assertIn('Pg1311TransitionTest',code)
        self.assertLess(code.index("+'.requested').open('x')"),code.index("if action=='stage':"))
        self.assertIn("'.requested']",code)
        self.assertNotIn('startsStopsReloadsEpochWrites0',code)
        self.assertNotIn('Pg1247',code)
        self.assertNotIn('pg1250',code)


if __name__=='__main__':unittest.main()
