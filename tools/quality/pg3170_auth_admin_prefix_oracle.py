"""Exact failed cohort prefix: three successful Login, DIF016 and one self UDT read."""
import collections
import datetime
from pg3136_browser_rows_oracle import TABLES, require, indexed, retained, without


def qualify(old, new, owner, lower, upper):
    require(set(old) == set(new) == TABLES and type(owner) is int and owner > 0, 'auth/UDT prefix all24')
    start, end = [datetime.datetime.fromisoformat(value.replace('Z', '+00:00')) for value in [lower, upper]]
    require(start.tzinfo is not None and end.tzinfo is not None and start <= end, 'auth/UDT window')
    def bounded(value):
        point = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(point.tzinfo is not None and start <= point <= end, 'auth/UDT timestamp')
    allowed = {'schubert.app_users', 'schubert.auth_sessions', 'schubert.login_ip_attempts', 'schubert.request_inbox', 'schubert.app_logs', 'schubert_web_session.web_http_sessions', 'schubert_web_session.web_log_outbox'}
    for table in TABLES - allowed:
        require(old[table] == new[table], 'auth/UDT no business/master/maintenance mutation ' + table)
    users, after_users = indexed(old['schubert.app_users'], 'id'), indexed(new['schubert.app_users'], 'id')
    require(users.keys() == after_users.keys() and owner in users, 'auth/UDT accounts')
    for identity, before in users.items():
        after = after_users[identity]
        if identity != owner:
            require(before == after, 'auth/UDT other account')
        else:
            fields = {'last_login_at', 'failed_count', 'failure_window_started_at', 'locked_until'}
            require(without(before, fields) == without(after, fields), 'auth/UDT protected account')
            require(after['role'] == 'ADMIN' and after['status'] == 'ACTIVE' and after['failed_count'] == 0 and after['failure_window_started_at'] is after['locked_until'] is None, 'auth/UDT successful Login')
            bounded(after['last_login_at'])
    a, b = indexed(old['schubert.auth_sessions'], 'id'), indexed(new['schubert.auth_sessions'], 'id')
    require(a.keys() <= b.keys(), 'auth/UDT original auth retained')
    replaced = 0
    for identity, before in a.items():
        after = b[identity]
        if before == after:
            continue
        require(before['user_id'] == owner and before['revoked'] is False and without(before, {'revoked', 'revoked_at', 'revoke_reason'}) == without(after, {'revoked', 'revoked_at', 'revoke_reason'}) and after['revoked'] is True and after['revoke_reason'] == 'REPLACED', 'auth/UDT prior owner replacement only')
        bounded(after['revoked_at']); replaced += 1
    fresh = [row for identity, row in b.items() if identity not in a]
    require(len(fresh) == 3 and all(row['user_id'] == owner for row in fresh), 'auth/UDT exactly three new owned sessions')
    require(collections.Counter(row['revoke_reason'] for row in fresh) == {'REPLACED': 1, None: 2}, 'auth/UDT fresh DIF016 reasons')
    for row in fresh:
        bounded(row['issued_at']); bounded(row['last_accessed_at'])
        if row['revoke_reason'] == 'REPLACED':
            require(row['revoked'] is True, 'auth/UDT replaced'); bounded(row['revoked_at'])
        else:
            require(row['revoked'] is False and row['revoked_at'] is None, 'auth/UDT two remain active')
    addresses = {row['client_address'] for row in fresh}; require(len(addresses) == 1, 'auth/UDT fixed client')
    ips, after_ips = indexed(old['schubert.login_ip_attempts'], 'client_address'), indexed(new['schubert.login_ip_attempts'], 'client_address')
    require(ips.keys() <= after_ips.keys(), 'auth/UDT IP retained')
    for address, row in after_ips.items():
        if address not in addresses:
            require(row == ips.get(address), 'auth/UDT other IP')
        else:
            require(row['failed_count'] == 0 and row['locked_until'] is None, 'auth/UDT clear current IP')
    inbox = retained(old['schubert.request_inbox'], new['schubert.request_inbox'], 'message_id')
    require(collections.Counter(row['request_layout_id'] for row in inbox) == {'LGNREQ01': 3, 'UDTREQ01': 1}, 'auth/UDT four exact Inbox rows')
    logins = {row['message_id']: row for row in inbox if row['request_layout_id'] == 'LGNREQ01'}
    require({row['created_message_id'] for row in fresh} == set(logins), 'auth/UDT three auth/Inbox identity join')
    for row in inbox:
        require(row['operation_token'] is None and row['processing_state'] == 'COMPLETED' and row['response_body_encrypted'] is not None, 'auth/UDT committed snapshots')
        bounded(row['created_at']); bounded(row['completed_at'])
        if row['request_layout_id'] == 'LGNREQ01':
            require(row['owner_user_id'] is None and row['response_layout_id'] == 'LGNRSP01' and row['result_ref_type'] == 'AUTH_SESSION' and row['result_ref_uuid'] in {r['id'] for r in fresh}, 'auth/UDT Login profile')
        else:
            require(row['owner_user_id'] == owner and row['response_layout_id'] == 'UDTRSP01' and row['result_ref_type'] == 'NONE' and row['result_ref_id'] is row['result_ref_uuid'] is None, 'auth/UDT owner read profile')
    web = retained(old['schubert_web_session.web_http_sessions'], new['schubert_web_session.web_http_sessions'])
    require(len(web) == 3 and all(row['max_inactive_seconds'] == 28800 for row in web), 'auth/UDT three Web sessions')
    for row in web:
        bounded(row['created_at']); bounded(row['last_accessed_at'])
    outbox = retained(old['schubert_web_session.web_log_outbox'], new['schubert_web_session.web_log_outbox'])
    logs = retained(old['schubert.app_logs'], new['schubert.app_logs'])
    sent, observed, actions = {}, set(), collections.Counter()
    for row in outbox:
        require(row['layout_id'] == 'WLGEVT01' and row['status'] == 'SENT' and row['lease_owner'] is row['lease_until'] is row['last_error_code'] is None and row['message_id'] not in sent, 'auth/UDT settled Web event')
        sent[row['message_id']] = row['correlation_id']; bounded(row['created_at']); bounded(row['sent_at'])
    for row in logs:
        require(row['service'] in {'WEB', 'API'} and row['actor_user_id'] in {None, owner} and row['level'] in {'INFO', 'WARN'}, 'auth/UDT audit scope')
        bounded(row['logged_at'])
        if row['source_message_id'] is not None:
            require(row['service'] == 'WEB' and row['category'] == 'REQUEST' and row['action'] == 'HTTP_REQUEST_COMPLETED' and row['message_id'] == row['source_message_id'] and row['message_id'] not in observed and sent.get(row['message_id']) == row['correlation_id'], 'auth/UDT Web audit identity')
            observed.add(row['message_id'])
        else:
            require(row['service'] == 'API' and row['category'] == 'SECURITY' and row['action'] in {'LOGIN_SUCCEEDED', 'SESSION_REVOKED'} and row['message_id'] in logins and row['correlation_id'] == logins[row['message_id']]['correlation_id'], 'auth/UDT Login/replacement audit identity')
            actions[row['action']] += 1
    require(sent and set(sent) == observed and actions['LOGIN_SUCCEEDED'] == 3 and actions['SESSION_REVOKED'] == replaced + 1, 'auth/UDT one-to-one and replacement counts')
    return {'all24PartialQualified': True, 'newLoginInbox': 3, 'newUdtInbox': 1, 'newAuthSessions': 3, 'newWebSessions': 3, 'newQuestions': 0, 'newSentWebLogs': len(outbox), 'oldBrowserActualExit': 1, 'failedCaseNormalized': False, 'formalAccepted': False, 'rawExported': False}
