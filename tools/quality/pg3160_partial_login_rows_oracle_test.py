"""Independent one-Login fixture and forbidden partial/unknown mutations."""
import copy
import unittest
from pg3136_browser_rows_oracle_test import fixture as full_fixture, T
from pg3160_partial_login_rows_oracle import qualify


def fixture():
    old, new = full_fixture()
    for name in ['questions', 'answers', 'async_jobs', 'notifications', 'mq_outbox']:
        new['schubert.' + name] = []
    new['schubert_web_session.web_receipt_references'] = []
    auth = new['schubert.auth_sessions'][0]
    auth.update(revoked=False, revoked_at=None, revoke_reason=None, created_message_id=0)
    new['schubert.auth_sessions'] = [auth]
    row = new['schubert.request_inbox'][0]
    row.update(result_ref_type='AUTH_SESSION', result_ref_uuid=1, correlation_id='login-wire')
    new['schubert.request_inbox'] = [row]
    new['schubert_web_session.web_http_sessions'] = new['schubert_web_session.web_http_sessions'][:1]
    new['schubert.app_logs'][0]['action'] = 'HTTP_REQUEST_COMPLETED'
    new['schubert.app_logs'].append({'id': 2, 'service': 'API', 'category': 'SECURITY', 'level': 'INFO', 'action': 'LOGIN_SUCCEEDED', 'actor_user_id': 1, 'logged_at': T, 'message_id': 0, 'correlation_id': 'login-wire', 'source_message_id': None})
    return old, new


class PartialLogin(unittest.TestCase):
    def qualify(self, old, new):
        return qualify(old, new, 1, '2026-10-15T02:00:00Z', '2026-10-15T02:02:00Z')

    def test_exact_one_login_does_not_normalize_failed_menu_or_create_question(self):
        old, new = fixture()
        result = self.qualify(old, new)
        self.assertTrue(result['all24PartialQualified'])
        self.assertEqual(1, result['oldBrowserActualExit'])
        self.assertFalse(result['failedCaseNormalized'])

    def test_unplanned_business_owner_and_audit_changes_refused(self):
        faults = [
            lambda v: v['schubert.questions'].append({'id': 9}),
            lambda v: v['schubert.request_inbox'][0].update(request_layout_id='QSBREQ01'),
            lambda v: v['schubert.request_inbox'][0].update(result_ref_uuid=2),
            lambda v: v['schubert.auth_sessions'][0].update(user_id=2),
            lambda v: v['schubert.auth_sessions'][0].update(revoked=True),
            lambda v: v['schubert.app_users'][0].update(password_hash='changed'),
            lambda v: v['schubert.app_logs'][-1].update(message_id='foreign'),
            lambda v: v['schubert.app_logs'][-1].update(action='USER_CREATED'),
            lambda v: v['schubert_web_session.web_log_outbox'][0].update(status='PENDING'),
            lambda v: v['schubert_web_session.web_http_sessions'].append(copy.deepcopy(v['schubert_web_session.web_http_sessions'][0])),
        ]
        for fault in faults:
            old, new = fixture(); fault(new)
            with self.assertRaises(ValueError):
                self.qualify(old, new)


if __name__ == '__main__':
    unittest.main()
