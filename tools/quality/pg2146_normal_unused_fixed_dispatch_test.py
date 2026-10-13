import unittest
import pg2146_normal_unused_fixed_dispatch as p


class Dispatch(unittest.TestCase):
    def test_actual_closed_new_slots(self):
        raw=p.source()
        self.assertIn('pg2145-frozen',raw)
        self.assertNotIn('pg2133-frozen',raw)
        self.assertIn('pg2146-',raw)
        self.assertIn('Pg2144UnusedStage',raw)
        self.assertNotIn('Pg2132UnusedStage',raw)
        self.assertIn('pg2146-fixed-stage-v1',p.STAGE)
        self.assertEqual(p.GUEST,'/var/lib/pgpt-s1-preservation/pg2144-current-normal-unused-tools-v1')
        self.assertEqual(p.REMOTE,'/home/ubuntu/pg2146-current-normal-input-v1')
        self.assertNotIn('daemon-reload',raw)


if __name__=='__main__':unittest.main()
