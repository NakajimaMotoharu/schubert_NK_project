import unittest
import pg2180_newsource_live_binding as p


class Binding(unittest.TestCase):
    def test_actual_current_entry_and_prior_completion_rejection(self):
        raw=p.body()
        self.assertIn('PG2126',raw);self.assertNotIn('PG1846',raw)
        for text in ['a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75','9026b2ab-bb42-49cd-a2bd-4c661049dce3']:self.assertIn(text,raw)
        fn=p.entry();self.assertEqual(fn.__globals__['SOURCE'],'3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8')
        self.assertEqual(fn.__globals__['SLOT'],'pg2180-newsource-live-binding-v1')
        self.assertNotIn('systemctl start',raw)


if __name__=='__main__':unittest.main()
