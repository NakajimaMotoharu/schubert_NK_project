import unittest
from unittest.mock import patch
import pg6016_constants_qualification as t


class IndependentCurrentWholeDefinitionTest(unittest.TestCase):
    def test_all_1666_exact_differences_and_candidate_bytes_required(self):
        before={str(i)+'.class':'a'*64 for i in range(1666)};after={**before,'0.class':'b'*64};kinds={'0.class':'SAME_VALUE_PRIVATE_CONSTANT'}
        with patch.object(t,'EXPECTED_OLD',before,create=True),patch.object(t,'EXPECTED_NEW',after,create=True),patch.object(t,'PHYSICAL_KINDS',kinds,create=True):
            differences,unchanged=t.physical_difference(before,after,after);self.assertEqual((1,1665),(len(differences),unchanged))
            for wrong in ({**after,'1.class':'c'*64},{k:v for k,v in after.items()if k!='0.class'}):
                with self.assertRaises(ValueError):t.physical_difference(before,wrong,wrong)
            with self.assertRaises(ValueError):t.physical_difference(before,after,before)

    def test_complete_bounded_reader_uses_file_payload_and_current_paths(self):
        raw=t.emitted('0'*64)
        for path in('runs/PG6014-six-v1','source-full-PG6014','runs/PG5944-six-v1','transfer/PG6014-source.tar','PG6016-qualified-v1/input.safe.json'):
            self.assertIn(path,raw)
        self.assertNotIn('runs/PG5926-six-v1',raw)
        self.assertIn("len(targets)!=67",raw);self.assertIn('allActualClassCounters',raw)


if __name__=='__main__':unittest.main()
