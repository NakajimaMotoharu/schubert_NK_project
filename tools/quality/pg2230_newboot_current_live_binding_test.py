import unittest
from pg2230_newboot_current_live_binding import compose


class ActualBinding(unittest.TestCase):
    def test_fixed_new_boot_and_dynamic_actual_generation_only(self):
        s=compose({'MainPID':'123','InvocationID':'1'*32,'ExecMainStartTimestampMonotonic':'500','Job':'12'})
        for v in ['b2d6f605-61cf-425f-8fbd-12d606f6ee66','b2d6f60561cf425f8fbd12d606f6ee66',
          '3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8','62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c',
          'active.read_bytes()==raw and show()==unit',"'startsStops0':True"]:self.assertIn(v,s)
        self.assertNotIn('3d69f5af',s)
        self.assertNotIn('02bddddf-9cd3-4668-9d67-7561232fc4e4',s)
        for invalid in [None,{}, {'MainPID':None}]:
            with self.assertRaises(ValueError):compose(invalid)


if __name__=='__main__':unittest.main()
