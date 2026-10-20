import unittest
from pg5798_lifetime_empty_review import empty_block


class ExactEmptyNotificationTest(unittest.TestCase):
    def test_comment_only_not_cleanup_or_retry(self):
        empty_block(') { /* observation only */\n // retained frame\n}',0)
        for body in(') {return;}',' ) { close(); }',') { flag = true; }'):
            with self.assertRaises(ValueError):empty_block(body,0)


if __name__=='__main__':unittest.main()
