"""SS314/324/331/351: exact one-Login prefix of the failed Menu cohort.

This never marks failed PT-NBR002 or the old Browser run as PASS. It only
authenticates the legitimate side effects before a separately fixed new cohort.
"""
import collections
import datetime
from pg3136_browser_rows_oracle import TABLES, require, indexed, retained, without


def qualify(old, new, owner, lower, upper):
    require(set(old) == set(new) == TABLES and type(owner) is int and owner > 0, 'partial all24 scope/owner')
    start, end = [datetime.datetime.fromisoformat(value.replace('Z', '+00:00')) for value in [lower, upper]]
    require(start.tzinfo is not None and end.tzinfo is not None and start <= end, 'partial event window')
    def bounded(value):
        point = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(point.tzinfo is not None and start <= point <= end, 'partial event timestamp')
    allowed = {'schubert.app_users', 'schubert.auth_sessions', 'schubert.login_ip_attempts', 'schubert.request_inbox', 'schubert.app_logs', 'schubert_web_session.web_http_sessions', 'schubert_web_session.web_log_outbox'}
    for table in TABLES - allowed:
        require(old[table] == new[table], 'partial no business/master/maintenance mutation ' + table)
    users, after_users = indexed(old['schubert.app_users'], 'id'), indexed(new['schubert.app_users'], 'id')
    require(users.keys() == after_users.keys() and owner in users, 'partial account identity')
    for identity, before in users.items():
        after = after_users[identity]
        if identity != owner:
            require(before == after, 'partial other account')
        else:
            columns = {'last_login_at', 'failed_count', 'failure_window_started_at', 'locked_until'}
            require(without(before, columns) == without(after, columns), 'partial protected account columns')
            require(after['role'] == 'ADMIN' and after['status'] == 'ACTIVE' and after['failed_count'] == 0 and after['failure_window_started_at'] is after['locked_until'] is None, 'partial successful Login')
            bounded(after['last_login_at'])
    before_auth, after_auth = indexed(old['schubert.auth_sessions'], 'id'), indexed(new['schubert.auth_sessions'], 'id')
    require(before_auth.keys() <= after_auth.keys(), 'partial no old auth deletion')
    for identity, before in before_auth.items():
        after = after_auth[identity]
        if before == after:
            continue
        require(before['user_id'] == owner and before['revoked'] is False and without(before, {'revoked', 'revoked_at', 'revoke_reason'}) == without(after, {'revoked', 'revoked_at', 'revoke_reason'}) and after['revoked'] is True and after['revoke_reason'] == 'REPLACED', 'partial only owner replacement')
        bounded(after['revoked_at'])
    auth = [row for identity, row in after_auth.items() if identity not in before_auth]
    require(len(auth) == 1 and auth[0]['user_id'] == owner and auth[0]['revoked'] is False and auth[0]['revoked_at'] is auth[0]['revoke_reason'] is None, 'partial exactly one live Login')
    bounded(auth[0]['issued_at']); bounded(auth[0]['last_accessed_at'])
    ips, after_ips = indexed(old['schubert.login_ip_attempts'], 'client_address'), indexed(new['schubert.login_ip_attempts'], 'client_address')
    require(ips.keys() <= after_ips.keys(), 'partial no IP removal')
    for address, row in after_ips.items():
        if address != auth[0]['client_address']:
            require(row == ips.get(address), 'partial other IP unchanged')
        else:
            require(row['failed_count'] == 0 and row['locked_until'] is None, 'partial current IP clear')
    inbox = retained(old['schubert.request_inbox'], new['schubert.request_inbox'], 'message_id')
    require(len(inbox) == 1, 'partial exactly one Inbox')
    row = inbox[0]
    require(row['request_layout_id'] == 'LGNREQ01' and row['owner_user_id'] is row['operation_token'] is None and row['processing_state'] == 'COMPLETED' and row['response_layout_id'] == 'LGNRSP01' and row['response_body_encrypted'] is not None and row['result_ref_type'] == 'AUTH_SESSION' and row['result_ref_uuid'] == auth[0]['id'], 'partial Login result profile')
    require(auth[0]['created_message_id'] == row['message_id'], 'partial auth/Inbox identity join')
    bounded(row['created_at']); bounded(row['completed_at'])
    web = retained(old['schubert_web_session.web_http_sessions'], new['schubert_web_session.web_http_sessions'])
    require(len(web) == 1 and web[0]['max_inactive_seconds'] == 28800, 'partial one authenticated Web session')
    bounded(web[0]['created_at']); bounded(web[0]['last_accessed_at'])
    logs = retained(old['schubert.app_logs'], new['schubert.app_logs'])
    outbox = retained(old['schubert_web_session.web_log_outbox'], new['schubert_web_session.web_log_outbox'])
    require(logs and outbox, 'partial real audit delivery')
    sent = {}
    for row in outbox:
        require(row['layout_id'] == 'WLGEVT01' and row['status'] == 'SENT' and row['lease_owner'] is row['lease_until'] is row['last_error_code'] is None and row['message_id'] not in sent, 'partial settled unique Web event')
        sent[row['message_id']] = row['correlation_id']; bounded(row['created_at']); bounded(row['sent_at'])
    observed, actions = set(), collections.Counter()
    for row in logs:
        require(row['service'] in {'WEB', 'API'} and row['actor_user_id'] in {None, owner} and row['level'] in {'INFO', 'WARN'}, 'partial audit service/actor')
        bounded(row['logged_at'])
        if row['source_message_id'] is not None:
            require(row['service'] == 'WEB' and row['category'] == 'REQUEST' and row['action'] == 'HTTP_REQUEST_COMPLETED' and row['source_message_id'] == row['message_id'] and sent.get(row['message_id']) == row['correlation_id'] and row['message_id'] not in observed, 'partial delivered Web event')
            observed.add(row['message_id'])
        else:
            require(row['service'] == 'API' and row['category'] == 'SECURITY' and row['action'] in {'LOGIN_SUCCEEDED', 'SESSION_REVOKED'}, 'partial API Login-only audit')
            require(row['message_id'] == inbox[0]['message_id'] and row['correlation_id'] == inbox[0]['correlation_id'], 'partial API audit/Inbox identity')
            actions[row['action']] += 1
    require(set(sent) == observed and actions['LOGIN_SUCCEEDED'] == 1, 'partial audit one-to-one and one success')
    return {'all24PartialQualified': True, 'newLoginInbox': 1, 'newAuthSessions': 1, 'newWebSessions': 1, 'newQuestions': 0, 'newSentWebLogs': len(outbox), 'oldBrowserActualExit': 1, 'failedCaseNormalized': False, 'formalAccepted': False, 'rawExported': False}
