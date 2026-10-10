import unittest
from pg1321_live_root_binding import BODY

class LiveRootBindingTest(unittest.TestCase):
    def test_complete_readonly_payload_checks_current_generation_twice(self):
        compile(BODY,'<complete actual original capture>','exec')
        self.assertIn("show()==unit",BODY)
        self.assertIn("unit['Job']==EXPECTED['Job']",BODY)
        self.assertIn('rootArgvSha256',BODY)
        self.assertIn('rawExported',BODY)
        self.assertNotIn("'start'",BODY.split('unit=show();')[0])
        self.assertNotIn('permit',BODY)
        self.assertNotIn('password',BODY)

if __name__=='__main__':unittest.main()
