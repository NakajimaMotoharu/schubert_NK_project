import unittest
from pg1457_current_day_binding import compose


class BindingTest(unittest.TestCase):
    def test_actual_generation_and_original_guards(self):
        s=compose({'MainPID':'6873','InvocationID':'1ee3b3e121c74e63ae28fe4d912e9ede','ExecMainStartTimestampMonotonic':'5711141318','Job':'13033'})
        self.assertIn('3d69f5af-6bac-46b1-a540-7591c4a79a0d',s)
        self.assertIn("'boot':'3d69f5af6bac46b1a5407591c4a79a0d'",s)
        self.assertNotIn('cbca8738',s)
        self.assertIn('active.read_bytes()==raw and show()==unit',s)
        self.assertIn("'startsStops0':True",s)

    def test_unknown_null_generation_refused(self):
        for bad in [None,{}, {'MainPID':None}]:
            with self.assertRaises(ValueError):compose(bad)


if __name__=='__main__':unittest.main()
