import unittest
from pyflakes.api import check
import pg2450_question_current_live_binding as binding


class ActualBinding(unittest.TestCase):
    def test_current_boot_new_run_and_nonmutating_entry(self):
        raw=binding.body()
        self.assertEqual(0,check("EXPECTED={}\nDIGEST='literal'\nSOURCE='literal'\n"+raw,'<whole actual live binding>'))
        for literal in ['b2d6f605-61cf-425f-8fbd-12d606f6ee66','b2d6f60561cf425f8fbd12d606f6ee66',
                        'PG2428','91f5484b-9702-4c7c-97f3-dd5110a853f9','e1429ac8-f3dd-4e8c-83d2-1926c4ba8440']:
            self.assertIn(literal,raw)
        self.assertNotIn('3d69f5af',raw)
        self.assertNotIn('systemctl start',raw)
        fn=binding.entry()
        self.assertEqual(fn.__globals__['SOURCE'],'cdbc07cdf77370d521e64de8b327da7f6752139b')
        self.assertEqual(fn.__globals__['SLOT'],'pg2450-question-current-live-binding-v1')


if __name__=='__main__':unittest.main()
