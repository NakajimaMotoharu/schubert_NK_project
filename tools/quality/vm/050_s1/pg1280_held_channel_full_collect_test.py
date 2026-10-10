import unittest
from pg1280_held_channel_full_collect import qualify_sessions


class TopologyTest(unittest.TestCase):
    def test_new_fixture_jvms_late_dump_and_all_boundaries(self):
        rows=[{'id':str(i),'start':'1000','dump':'1010'}for i in range(6)]+[{'id':'5','start':'1000','dump':'1020'}]
        self.assertEqual(qualify_sessions(rows,1,2,'bootstrap'),{'dumpRecords':7,'distinctSessions':6})
        for bad in [rows[:-1],rows[:-1]+[rows[-2]],rows[:-1]+[dict(rows[-1],start='1001')],rows[:-1]+[dict(rows[-1],dump='9999')],rows[:-1]+[dict(rows[-1],extra='unknown')]]:
            with self.assertRaises(ValueError):qualify_sessions(bad,1,2,'bootstrap')
        with self.assertRaises(ValueError):qualify_sessions(rows,1,2,'foreign')


if __name__=='__main__':unittest.main()
