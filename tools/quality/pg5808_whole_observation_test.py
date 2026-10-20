import unittest
from pg5808_whole_observation import SOURCE,observer_source


class Original3955OwnerBindingTest(unittest.TestCase):
    def test_source_archive_counts_and_lowercase_script_all_fixed(self):
        begin={'source':SOURCE,'tests':3955,'suites':587,'mainClasses':1665,'archiveSha256':'a'*64};raw=observer_source(begin)
        self.assertIn('pg5808-full.py',raw);self.assertIn(SOURCE,raw);self.assertIn('a'*64,raw)
        self.assertNotIn('pg5754',raw);self.assertNotIn('PG5754',raw)
        for key,value in(('tests',3939),('source','0'*40),('archiveSha256','bad')):
            with self.assertRaises(ValueError):observer_source({**begin,key:value})


if __name__=='__main__':unittest.main()
