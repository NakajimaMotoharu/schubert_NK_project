"""Literal newday session-before-inbox and query vectors independent of Production."""
import copy
import unittest
from pyflakes.api import check, checkPath
from pg4632_current_new_day_rows_oracle_test import fixture
from pg2078_current_same_day_rows_oracle_test import RUN, CUT, UPPER
from pg4742_same_day_query_oracle_test import Queries
import pg5030_new_day_query_oracle as oracle


def vectors():
    before, after = fixture()
    _, row, _ = Queries().fixture()
    before['schubert.request_inbox'].append(row)
    p = after['schubert.inbox_inspection_progress'][0]
    p.update(inspected_count=2, deleted_count=1, after_message_id=row['message_id'])
    batch = next(r for r in after['schubert.batch_runs'] if r['run_id'] == RUN and r['step'] == 'CLEAN_INBOX_OUTBOX')
    batch.update(target_count=3, success_count=2)
    return before, after, row


class NewDayQuery(unittest.TestCase):
    def test_new_day_deletes_selected_sessions_notifications_query_and_preserves_auth_reference(self):
        before, after, _ = vectors()
        ns = oracle.namespace(bytes(32))
        result = ns['qualify_current'](before, after, RUN, CUT, UPPER)
        self.assertEqual((10, 2, 1, 1, 1), (result['newDaySteps'], result['expectedSessionDeleted'],
                         result['expectedOutboxDeleted'], result['expectedInboxDeleted'], result['expectedInboxProtected']))
        self.assertEqual(1, result['newAnonymousHttpLogs'])
        self.assertFalse(result['wholeAccepted'])

    def test_wrong_cleanup_attempt_progress_retained_query_and_same_day_refused(self):
        before, after, row = vectors()
        ns = oracle.namespace(bytes(32))
        for mutate in [lambda a: a['schubert.request_inbox'].append(row),
                       lambda a: a['schubert.inbox_inspection_progress'][0].update(deleted_count=0),
                       lambda a: a['schubert.batch_runs'][12].update(attempt=2),
                       lambda a: a['schubert.notifications'].clear()]:
            bad = copy.deepcopy(after)
            mutate(bad)
            with self.assertRaises(ValueError):
                ns['qualify_current'](before, bad, RUN, CUT, UPPER)
        bad = copy.deepcopy(before)
        bad['schubert.batch_runs'][0]['business_date'] = '2026-10-13'
        with self.assertRaises(ValueError):
            ns['qualify_current'](bad, after, RUN, CUT, UPPER)

    def test_authenticated_cipher_unknown_layout_and_unremoved_session_refused(self):
        before, _, row = vectors()
        ns = oracle.namespace(bytes(32))
        expected = ns['candidates'](before, CUT)
        for changes in [('response_body_encrypted', '\\x00'), ('response_layout_id', 'UNKNOWN')]:
            bad = copy.deepcopy(before)
            bad['schubert.request_inbox'][-1][changes[0]] = changes[1]
            with self.assertRaises(ValueError):
                ns['expected_inbox'](bad, expected)
        bad = copy.deepcopy(before)
        bad['schubert.auth_sessions'][0]['expires_at'] = '2026-10-20T00:00:00Z'
        expected = ns['candidates'](bad, CUT)
        with self.assertRaises(ValueError):
            ns['expected_inbox'](bad, expected)
        self.assertEqual(row['response_layout_id'], 'QSDRSP01')

    def test_emitted_static_and_no_production_oracle_or_same_day_assumption(self):
        raw = oracle.source()
        self.assertEqual(0, check('KEY=bytes(32)\n' + raw, '<independent full24 oracle>'))
        self.assertNotIn('require(all(history.values()))', raw)
        self.assertIn("not any(row['business_date']==day", raw)
        self.assertNotIn('dev.codex.schubert.nk.', raw)
        self.assertEqual(0, checkPath(__file__))
        self.assertEqual(0, checkPath(oracle.__file__))


if __name__ == '__main__':
    unittest.main()
