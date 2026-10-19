"""BUG1480/YKT1241: never collapse distinct columns, meanings or raw occurrences."""
import unittest
import xml.etree.ElementTree as ET
from pmd_diagnostic_identity import diagnostic_row


class DiagnosticIdentityTest(unittest.TestCase):
    def row(self,column='31',text='RuntimeException',ordinal=1):
        v=ET.Element('violation',rule='AvoidCatchingGenericException',beginline='271',endline='271',begincolumn=column,endcolumn='55',priority='3');v.text=text
        return diagnostic_row('src/example.java','a'*64,v,ordinal)

    def test_distinct_columns_retain_old_collision_and_new_unique_ids(self):
        a,b=self.row(),self.row(column='50')
        self.assertEqual(a['legacyFindingId'],b['legacyFindingId'])
        self.assertNotEqual(a['findingId'],b['findingId'])

    def test_meaning_and_exact_duplicate_occurrence_are_distinct(self):
        a=self.row()
        self.assertNotEqual(a['findingId'],self.row(text='Error')['findingId'])
        self.assertNotEqual(a['findingId'],self.row(ordinal=2)['findingId'])

    def test_same_inputs_stable_and_nonpositive_ordinal_rejected(self):
        self.assertEqual(self.row(),self.row())
        with self.assertRaises(ValueError):self.row(ordinal=0)


if __name__=='__main__':unittest.main()
