"""Independent synthetic all24 fixture, no DB/VM/Production fixture generator."""
import copy
import unittest
from pg3136_browser_rows_oracle import qualify, TABLES

T = '2026-10-15T02:01:00+00:00'


def fixture():
    old = {name: [] for name in TABLES}
    old['schubert.app_users'] = [{'id': 1, 'role': 'ADMIN', 'status': 'ACTIVE', 'password_hash': 'synthetic-not-secret', 'version': 7, 'last_login_at': None, 'failed_count': 0, 'failure_window_started_at': None, 'locked_until': None}]
    new = copy.deepcopy(old)
    new['schubert.app_users'][0]['last_login_at'] = T
    new['schubert.questions'] = [{'id': 9, 'owner_user_id': 1, 'body': 'PG3128 native 質問 <b>独立oracle</b>', 'operation_token': 'synthetic', 'receipt_id': 'synthetic', 'submitted_at': T, 'is_deleted': False, 'deleted_at': None, 'deleted_by': None, 'version': 0}]
    new['schubert.async_jobs'] = [{'id': 10, 'question_id': 9, 'owner_user_id': 1, 'state': 'RECEIVED', 'retry_count': 0, 'message_id': 'job-event', 'correlation_id': 'job-correlation'}]
    new['schubert.notifications'] = [{'id': 11, 'job_id': 10, 'question_id': 9, 'owner_user_id': 1, 'state': 'RECEIVED'}]
    new['schubert_web_session.web_receipt_references'] = [{'receipt_id': 'synthetic', 'question_id': 9, 'submitted_at': T}]
    new['schubert.auth_sessions'] = [{'id': i, 'user_id': 1, 'revoked': True, 'revoke_reason': reason, 'issued_at': T, 'last_accessed_at': T, 'revoked_at': T, 'client_address': '192.0.2.1'} for i, reason in [(1, 'REPLACED'), (2, 'LOGOUT'), (3, 'LOGOUT')]]
    new['schubert.login_ip_attempts'] = [{'client_address': '192.0.2.1', 'failed_count': 0, 'locked_until': None}]
    layouts = ['LGNREQ01'] * 3 + ['LOGREQ01'] * 2 + ['QSBREQ01', 'UDTREQ01', 'QSDREQ01', 'QSDREQ01', 'NTSREQ01']
    new['schubert.request_inbox'] = [{'message_id': i, 'request_layout_id': layout, 'processing_state': 'COMPLETED', 'completed_at': T, 'response_body_encrypted': 'synthetic', 'owner_user_id': None if layout == 'LGNREQ01' else 1, 'operation_token': 'synthetic' if layout == 'QSBREQ01' else None, 'created_at': T, 'result_ref_type': 'NONE', 'result_ref_id': None, 'result_ref_uuid': None, 'response_layout_id': layout.replace('REQ', 'RSP'), 'request_version': '001', 'response_version': '001'} for i, layout in enumerate(layouts)]
    new['schubert.mq_outbox'] = [{'id': 1, 'destination': 'nk.async.work', 'layout_id': 'QWKREQ01', 'message_id': 'job-event', 'correlation_id': 'job-correlation', 'status': 'SENT', 'lease_owner': None, 'lease_until': None}]
    new['schubert_web_session.web_http_sessions'] = [{'id': i, 'max_inactive_seconds': 28800, 'created_at': T, 'last_accessed_at': T} for i in range(3)]
    new['schubert_web_session.web_log_outbox'] = [{'id': 1, 'message_id': 'log-event', 'correlation_id': 'log-event', 'layout_id': 'WLGEVT01', 'layout_version': '001', 'status': 'SENT', 'lease_owner': None, 'lease_until': None, 'last_error_code': None, 'created_at': T, 'sent_at': T}]
    new['schubert.app_logs'] = [{'id': 1, 'service': 'WEB', 'category': 'REQUEST', 'level': 'INFO', 'actor_user_id': 1, 'logged_at': T, 'message_id': 'log-event', 'correlation_id': 'log-event', 'source_message_id': 'log-event'}]
    return old, new


class BrowserRows(unittest.TestCase):
    def qualify(self, old, new):
        return qualify(old, new, 1, '2026-10-15T02:00:00Z', '2026-10-15T02:02:00Z')

    def test_literal_positive_and_optional_invalid_context_coordination(self):
        old, new = fixture()
        self.assertTrue(self.qualify(old, new)['all24Qualified'])
        extra = copy.deepcopy(new['schubert.request_inbox'][3]); extra['message_id'] = 20
        new['schubert.request_inbox'].append(extra)
        self.assertTrue(self.qualify(old, new)['all24Qualified'])

    def test_authenticated_business_correlation_is_not_self_event_id(self):
        old, new = fixture()
        new['schubert_web_session.web_log_outbox'][0]['correlation_id'] = 'first-business-wire'
        new['schubert.app_logs'][0]['correlation_id'] = 'first-business-wire'
        self.assertTrue(self.qualify(old, new)['all24Qualified'])
        new['schubert.app_logs'][0]['correlation_id'] = 'foreign-wire'
        with self.assertRaises(ValueError):
            self.qualify(old, new)

    def test_read_snapshots_are_required_not_arbitrary_extra_updates(self):
        for layout in ['UDTREQ01', 'QSDREQ01', 'NTSREQ01']:
            old, new = fixture()
            selected = next(row for row in new['schubert.request_inbox'] if row['request_layout_id'] == layout)
            for field, bad in [('owner_user_id', 2), ('result_ref_type', 'USER'), ('operation_token', 'foreign'), ('response_layout_id', 'UPWRSP01'), ('response_version', '002')]:
                changed = copy.deepcopy(new); row = next(r for r in changed['schubert.request_inbox'] if r['message_id'] == selected['message_id']); row[field] = bad
                with self.assertRaises(ValueError):
                    self.qualify(old, changed)
            changed = copy.deepcopy(new); changed['schubert.request_inbox'].remove(selected)
            with self.assertRaises(ValueError):
                self.qualify(old, changed)
            changed = copy.deepcopy(new); extra = {**selected, 'message_id': 21}; changed['schubert.request_inbox'].append(extra)
            with self.assertRaises(ValueError):
                self.qualify(old, changed)

    def test_each_forbidden_delta_is_independently_rejected(self):
        changes = [
            lambda v: v['schubert.games'].append({'id': 1}),
            lambda v: v['schubert.app_users'][0].update(role='USER'),
            lambda v: v['schubert.app_users'][0].update(password_hash='changed'),
            lambda v: v['schubert.questions'][0].update(body='wrong'),
            lambda v: v['schubert.questions'][0].update(owner_user_id=2),
            lambda v: v['schubert.notifications'][0].update(owner_user_id=2),
            lambda v: v['schubert.auth_sessions'][0].update(revoke_reason='LOGOUT'),
            lambda v: v['schubert.request_inbox'][0].update(request_layout_id='UPWREQ01'),
            lambda v: v['schubert.request_inbox'][5].update(operation_token='foreign'),
            lambda v: v['schubert.mq_outbox'][0].update(message_id='foreign'),
            lambda v: v['schubert_web_session.web_receipt_references'][0].update(owner_user_id=1),
            lambda v: v['schubert_web_session.web_http_sessions'][0].update(max_inactive_seconds=1),
            lambda v: v['schubert_web_session.web_log_outbox'][0].update(status='PENDING'),
            lambda v: v['schubert.app_logs'][0].update(source_message_id='foreign'),
            lambda v: v['schubert.app_logs'][0].update(logged_at='2026-10-15T03:00:00Z'),
        ]
        for change in changes:
            old, new = fixture(); change(new)
            with self.assertRaises(ValueError):
                self.qualify(old, new)

    def test_prior_rows_are_not_hidden_by_per_table_addition_allowlist(self):
        for table, key in [('schubert.questions', 'id'), ('schubert.request_inbox', 'message_id'), ('schubert_web_session.web_log_outbox', 'id')]:
            old, new = fixture()
            original = {key: 100, 'fixed': 'original'}
            old[table].append(original)
            new[table].append({**original, 'fixed': 'corrupt'})
            with self.assertRaises(ValueError):
                self.qualify(old, new)


if __name__ == '__main__':
    unittest.main()
