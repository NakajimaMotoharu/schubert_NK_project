import unittest
from pg2226_newboot_fresh_day_before import payload


class TrueDayBefore(unittest.TestCase):
    def test_all_prior_post_and_no_same_day_replay(self):
        s=payload()
        for v in ['pg2226-newboot-fresh-day-before-v1','PG2226-newboot-fresh-day-before-v1',
          '0.1.0-PG2126','require(len(same_day)==0)',"'existingSuccessfulInspectorStepsForDate':0",'ordinary_argv',
          "first==before['current'] and first==snapshot()","'permissionIssued':False"]:
            self.assertIn(v,s)
        self.assertNotIn('0.1.0-PG1292',s)
        self.assertNotIn('systemctl start',s)
        self.assertNotIn('invalidate(',s)


if __name__=='__main__':unittest.main()
