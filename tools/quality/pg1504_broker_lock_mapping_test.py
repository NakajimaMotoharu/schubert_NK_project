import unittest
from pg1504_broker_lock_mapping import validate,fixed_mapping

class BrokerMappingTest(unittest.TestCase):
    def fixture(self):
        return ['1: POSIX ADVISORY WRITE 41805 fd:01:51 0 EOF','2: POSIX ADVISORY WRITE 41805 fd:01:52 0 EOF','3: FLOCK ADVISORY WRITE 41805 00:21:31 0 EOF'],[(253,1,51),(253,1,52)],['100000-108000 rw-s 00000000 00:21 31 /tmp/hsperfdata_schubert-artemis/41805']
    def test_two_fd_one_mmap_without_invented_fd(self):
        a,b,c=self.fixture();self.assertEqual(3,len(validate(a,41805,b,c)))
        self.assertEqual((0,33,31),fixed_mapping(c,41805,(0,33,31))['key'])
    def test_missing_duplicate_foreign_and_mode_offset_path_span(self):
        a,b,c=self.fixture()
        for aa,bb,cc in [(a[:-1],b,c),(a+[a[0]],b,c),(a,b[:-1],c),(a,b,[]),(a,b,c+c),(a,b,[c[0].replace('rw-s','rw-p')]),(a,b,[c[0].replace('00000000','00001000')]),(a,b,[c[0].replace('41805','41806')]),(a,b,[c[0].replace('hsperfdata','foreign')]),(a,b,[c[0].replace('108000','107000')]),([a[0].replace('WRITE','READ'),*a[1:]],b,c),([a[0].replace('POSIX','OFDLCK'),*a[1:]],b,c),(a,b,[c[0].replace('00:21','00:22')])]:
            with self.assertRaises(ValueError):validate(aa,41805,bb,cc)
        for pid in (None,True,0,1,41806):
            with self.assertRaises(ValueError):validate(a,pid,b,c)

if __name__=='__main__':unittest.main()
