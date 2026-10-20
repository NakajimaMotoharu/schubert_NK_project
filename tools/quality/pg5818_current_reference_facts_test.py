import unittest
from pg5818_current_reference_facts import SOURCE,inputs,namespace


class CurrentTypeNamespaceTest(unittest.TestCase):
    def test_current_input_and_slot_no_historical_override(self):
        value=namespace()
        self.assertEqual(SOURCE,value['SOURCE'])
        self.assertEqual('pg5818-current-reference-facts-v1',value['SLOT'])
        self.assertIs(inputs,value['inputs'])
        self.assertTrue((value['TC']/'jdk-25.0.4/bin/javac').is_file())
        self.assertTrue((value['TC']/'jdk-25.0.4/bin/java').is_file())


if __name__=='__main__':unittest.main()
