"""Literal three-Login/one-read prefix with an older active retained session."""
import copy
import unittest
from pg3160_partial_login_rows_oracle_test import fixture as first_fixture
from pg3136_browser_rows_oracle_test import T
from pg3170_auth_admin_prefix_oracle import qualify


def fixture():
    _, old = first_fixture(); new = copy.deepcopy(old)
    new['schubert.auth_sessions'][0].update(revoked=True, revoked_at=T, revoke_reason='REPLACED')
    for index, identity in enumerate([11, 12, 13]):
        row = copy.deepcopy(old['schubert.auth_sessions'][0])
        row.update(id=identity, created_message_id=100+index, revoked=index==0, revoked_at=T if index==0 else None, revoke_reason='REPLACED' if index==0 else None)
        new['schubert.auth_sessions'].append(row)
        inbox = copy.deepcopy(old['schubert.request_inbox'][0]); inbox.update(message_id=100+index, correlation_id='login-'+str(index), result_ref_uuid=identity)
        new['schubert.request_inbox'].append(inbox)
        audit = copy.deepcopy(old['schubert.app_logs'][-1]); audit.update(id=10+index, message_id=100+index, correlation_id='login-'+str(index))
        new['schubert.app_logs'].append(audit)
        if index:
            revoked = copy.deepcopy(audit); revoked.update(id=20+index, action='SESSION_REVOKED'); new['schubert.app_logs'].append(revoked)
        web = copy.deepcopy(old['schubert_web_session.web_http_sessions'][0]); web['id']=10+index; new['schubert_web_session.web_http_sessions'].append(web)
    query = copy.deepcopy(old['schubert.request_inbox'][0]); query.update(message_id=103, correlation_id='udt', request_layout_id='UDTREQ01', owner_user_id=1, response_layout_id='UDTRSP01', result_ref_type='NONE', result_ref_uuid=None, result_ref_id=None)
    new['schubert.request_inbox'].append(query)
    event = copy.deepcopy(old['schubert_web_session.web_log_outbox'][0]); event.update(id=2, message_id='new-log', correlation_id='udt'); new['schubert_web_session.web_log_outbox'].append(event)
    log = copy.deepcopy(old['schubert.app_logs'][0]); log.update(id=30, message_id='new-log', source_message_id='new-log', correlation_id='udt'); new['schubert.app_logs'].append(log)
    return old, new


class AuthAdminPrefix(unittest.TestCase):
    def qualify(self, old, new):return qualify(old, new, 1, '2026-10-15T02:00:00Z', '2026-10-15T02:02:00Z')

    def test_exact_prefix_keeps_both_failed_runs_unaccepted(self):
        old,new=fixture();result=self.qualify(old,new)
        self.assertEqual((3,1,0),(result['newLoginInbox'],result['newUdtInbox'],result['newQuestions']))
        self.assertEqual(1,result['oldBrowserActualExit']);self.assertFalse(result['failedCaseNormalized'])

    def test_each_unplanned_update_or_missing_identity_is_refused(self):
        faults=[lambda v:v['schubert.questions'].append({'id':9}),lambda v:v['schubert.request_inbox'][-1].update(request_layout_id='UPWREQ01'),lambda v:v['schubert.auth_sessions'][-1].update(revoked=True),lambda v:v['schubert.app_users'][0].update(role='USER'),lambda v:v['schubert.app_logs'][-1].update(correlation_id='foreign'),lambda v:v['schubert.request_inbox'][-1].update(owner_user_id=2)]
        for fault in faults:
            old,new=fixture();fault(new)
            with self.assertRaises(ValueError):self.qualify(old,new)


if __name__=='__main__':unittest.main()
