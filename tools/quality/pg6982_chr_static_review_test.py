import unittest
import xml.etree.ElementTree as ET

import pg6980_chr_path_qualification as q
import pg6982_chr_static_review as p


class CommonQualificationTest(unittest.TestCase):
    def test_embedded_position_is_validated_not_arbitrary_message_digits_removed(self):
        row=dict(rule='AvoidDuplicateLiterals',beginline='12',message='The String literal "field" appears 4 times in this file; the first occurrence is on line 12')
        moved={**row,'beginline':'15','message':row['message'].replace('line 12','line 15')}
        self.assertEqual(p.semantic_identity(row),p.semantic_identity(moved))
        self.assertNotEqual(p.semantic_identity(row),p.semantic_identity({**row,'message':row['message'].replace('4 times','5 times')}))
        self.assertNotEqual(p.semantic_identity(row),p.semantic_identity({**row,'message':row['message'].replace('"field"','"other"')}))
        for changed in ({**row,'beginline':'13'},{**row,'message':'unknown format'}):
            with self.assertRaises(ValueError):p.semantic_identity(changed)

    def test_real_positive_four_and_refuse_missing_missed_zero_dimensions(self):
        rows=[ET.Element('counter',type=k,missed='0',covered='1') for k in q.TYPES]
        self.assertEqual(4,len(q.counters(rows)))
        for change in ('missing','missed','zero'):
            copy=[ET.Element('counter',**x.attrib) for x in rows]
            if change=='missing':copy.pop()
            elif change=='missed':copy[0].set('missed','1')
            else:copy[0].set('covered','0')
            with self.assertRaises(ValueError):q.counters(copy)

    def test_unknown_rule_and_real_arbitrary_input_np_never_classified_safe(self):
        self.assertEqual('FALSE_POSITIVE',p.classify_spot('NP_NULL_ON_SOME_PATH_FROM_RETURN_VALUE','GateCli','lambda$caseIds$0')[0])
        for method in ('preflight','writeJson','promoteCurrent','unknown'):
            with self.assertRaises(ValueError):p.classify_spot('NP_NULL_ON_SOME_PATH_FROM_RETURN_VALUE','GateCli',method)
        with self.assertRaises(ValueError):p.classify_pmd({'rule':'UnknownSecurityRule'})
        with self.assertRaises(ValueError):p.classify_spot('OTHER','GateCli','preflight')


if __name__=='__main__':
    unittest.main()
