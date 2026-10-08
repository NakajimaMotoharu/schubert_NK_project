"""New genuine normal completion, no business or VM actions."""
import unittest
from pg653_capture_done import payload


class Binding(unittest.TestCase):
    def test_literal_new_cohort_genuine_receipt_and_owned_unit_windows(self):
        raw=payload('aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee');compile(raw,'<new receipt>','exec')
        for text in ('107901545407','1826480','111752','095f6d1d7f8442b7b2b44ae59a4314f5',
                     'pg653-completed-readonly-v1','pg650-fresh-parent-v2',"baseline['bounds']['lower']",'metadata9(p.lstat())==metadata9(s)',
                     'ownedUnits','parentEndedUTC',"env['completed'](pid1,done)",'manager.UnrefUnit(u)','bus.close()'):
            self.assertIn(text,raw)
        for text in ('e49243d5','p.lstat()==s','daemon-reload','.unlink(',"['systemctl','start'","['systemctl','stop'"):
            self.assertNotIn(text,raw)
        for old in ('e49243d5-de84-4714-8612-6912ddc17e9e','3a53b979-fa01-47dd-92a6-7b26affcfb5c','aaaaaaaa-bbbb-1ccc-8ddd-eeeeeeeeeeee'):
            with self.subTest(run=old),self.assertRaises(AssertionError):payload(old)


if __name__=='__main__':unittest.main()
