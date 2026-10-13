import unittest
import pg2190_newsource_owned_stop_dispatch as p


class OwnedStop(unittest.TestCase):
    def test_entire_newsource_current_stage_and_action_namespace(self):
        for text in ['0.1.0-PG2126','3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8','62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c',p.GUEST,p.ARCHIVE]:self.assertIn(text,p.STAGE)
        self.assertNotIn('0.1.0-PG1846',p.STAGE)
        raw=p.run_source()
        for text in ['pg2189','pg2190','pg2191','pg2192-newsource-pre-stop-full-v1','Pg2188','PG2126']:self.assertIn(text,raw)
        self.assertNotIn('pg2091',raw)
        self.assertNotIn('PG1846',raw)


if __name__=='__main__':unittest.main()
