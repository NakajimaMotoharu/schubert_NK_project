"""Conservative lifecycle scan; unknown compound ownership is not a PASS."""
import unittest

from db_fixture_lifecycle_audit import inspect_source


class LifecycleScan(unittest.TestCase):
    def source(self, body):
        return 'class T { private static BatchDatabaseFixture db; @AfterAll static void end() {' + body + '} }'

    def test_plain_stop_needs_guard_but_both_lexical_guards_pass(self):
        self.assertEqual('UNGUARDED_SIMPLE', inspect_source(self.source('db.stop();'))[0]['status'])
        for body in ['if (db != null) db.stop();', 'if(db!=null){db.stop();}']:
            self.assertEqual('GUARDED', inspect_source(self.source(body))[0]['status'])

    def test_unrelated_guard_and_compound_body_are_not_accepted(self):
        for body in ['if(db!=null) {} db.stop();', 'doOther(); db.stop();']:
            self.assertEqual('MANUAL_REVIEW', inspect_source(self.source(body))[0]['status'])

    def test_comments_and_literals_do_not_create_lifecycle_candidates(self):
        self.assertEqual([], inspect_source('class T { String x="@AfterAll { db.stop(); }"; }'))
        self.assertEqual('NO_NULLABLE_STATIC_DB_STOP', inspect_source(self.source('broker.stop();'))[0]['status'])

    def test_guarded_db_does_not_hide_unguarded_nullable_crypto_owner(self):
        raw = self.source('codec.close(); if(db!=null)db.stop();').replace(
            'private static BatchDatabaseFixture db;',
            'private static BatchDatabaseFixture db; private static AuthContextCodec codec;')
        row = inspect_source(raw)[0]
        self.assertEqual('GUARDED', row['status'])
        self.assertEqual([('codec', False), ('db', True)], [(c['field'], c['guarded']) for c in row['cleanupCalls']])


if __name__ == '__main__':
    unittest.main()
