"""Independent UI224/226 + SS314/323/331/351 finite Browser all24 delta.

No Production methods, mutation authority, observed-to-expected regeneration, or
coverage acceptance. Input is private consistent SQL snapshots; output has counts only.
"""
import collections
import datetime
import json
from pathlib import Path
from pg543_retirement_contract import TABLES

BODY = 'PG3128 native 質問 <b>独立oracle</b>'


def require(value, label):
    if not value:
        raise ValueError('finite Browser SQL oracle: ' + label)


def without(row, keys):
    return {key: value for key, value in row.items() if key not in keys}


def indexed(rows, key):
    require(type(rows) is list and all(type(row) is dict and key in row for row in rows), 'typed rows')
    result = {row[key]: row for row in rows}
    require(len(result) == len(rows), 'unique row identity')
    return result


def retained(old, new, key='id'):
    before, after = indexed(old, key), indexed(new, key)
    require(all(after.get(identity) == row for identity, row in before.items()), 'old rows unchanged')
    return [row for identity, row in after.items() if identity not in before]


def qualify(old, new, owner, lower, upper):
    require(type(owner) is int and owner > 0, 'fixed authenticated owner')
    require(type(old) is dict and type(new) is dict and set(old) == set(new) == TABLES, 'all24 exact scope')
    start = datetime.datetime.fromisoformat(lower.replace('Z', '+00:00'))
    end = datetime.datetime.fromisoformat(upper.replace('Z', '+00:00'))
    require(start.tzinfo is not None and end.tzinfo is not None and start <= end, 'bounded independent window')
    def bounded(value):
        point = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(point.tzinfo is not None and start <= point <= end, 'event time window')
    mutable = {'schubert.' + name for name in ['answers', 'app_logs', 'app_users', 'async_jobs', 'auth_sessions', 'login_ip_attempts', 'mq_outbox', 'notifications', 'questions', 'request_inbox']}
    mutable |= {'schubert_web_session.' + name for name in ['web_http_sessions', 'web_log_outbox', 'web_receipt_references']}
    for table in TABLES - mutable:
        require(old[table] == new[table], 'immutable table ' + table)
    before_users = indexed(old['schubert.app_users'], 'id')
    after_users = indexed(new['schubert.app_users'], 'id')
    require(before_users.keys() == after_users.keys() and owner in before_users, 'no account creation/deletion')
    for identity, row in before_users.items():
        now = after_users[identity]
        if identity != owner:
            require(row == now, 'other account unchanged')
        else:
            require(without(row, {'last_login_at', 'failed_count', 'failure_window_started_at', 'locked_until'}) == without(now, {'last_login_at', 'failed_count', 'failure_window_started_at', 'locked_until'}), 'protected account columns')
            require(now['role'] == 'ADMIN' and now['status'] == 'ACTIVE' and now['failed_count'] == 0 and now['failure_window_started_at'] is None and now['locked_until'] is None, 'successful Login counters')
            bounded(now['last_login_at'])
    added = {}
    special_keys = {'schubert.request_inbox': 'message_id', 'schubert_web_session.web_receipt_references': 'receipt_id'}
    for table in mutable - {'schubert.app_users', 'schubert.auth_sessions', 'schubert.login_ip_attempts'}:
        added[table] = retained(old[table], new[table], special_keys.get(table, 'id'))
    questions = added['schubert.questions']
    require(len(questions) == 1, 'one new question')
    question = questions[0]
    qid, token = question['id'], question['operation_token']
    require(question['owner_user_id'] == owner and question['body'] == BODY and question['is_deleted'] is False and question['deleted_at'] is question['deleted_by'] is None and question['version'] == 0, 'literal question and owner')
    bounded(question['submitted_at'])
    jobs, notices, answers = (added['schubert.' + name] for name in ['async_jobs', 'notifications', 'answers'])
    require(len(jobs) == len(notices) == 1 and len(answers) <= 1, 'one job and owner notification')
    job, notice = jobs[0], notices[0]
    require(job['question_id'] == notice['question_id'] == qid and job['owner_user_id'] == notice['owner_user_id'] == owner and notice['job_id'] == job['id'], 'business FK owner join')
    require(job['state'] in {'RECEIVED', 'PROCESSING', 'COMPLETED', 'ERROR'} and notice['state'] == job['state'], 'legal asynchronous state, not fake deterministic completion')
    require(type(job['retry_count']) is int and 0 <= job['retry_count'] <= 3, 'bounded retry')
    for answer in answers:
        require(answer['question_id'] == qid and answer['provider_type'] in {'STUB', 'EXTERNAL_AI'} and answer['is_deleted'] is False, 'new answer scope only; provider semantics separately unaccepted')
    require(bool(answers) == (job['state'] == 'COMPLETED'), 'answer/state relation')
    refs = added['schubert_web_session.web_receipt_references']
    require(len(refs) == 1 and set(refs[0]) == {'receipt_id', 'question_id', 'submitted_at'} and refs[0]['receipt_id'] == question['receipt_id'] and refs[0]['question_id'] == qid, 'immutable three-column locator')
    a = datetime.datetime.fromisoformat(question['submitted_at'].replace('Z', '+00:00'))
    b = datetime.datetime.fromisoformat(refs[0]['submitted_at'].replace('Z', '+00:00'))
    require(a.replace(microsecond=a.microsecond // 1000 * 1000) == b, 'locator UTC milliseconds')
    before_auth = indexed(old['schubert.auth_sessions'], 'id')
    after_auth = indexed(new['schubert.auth_sessions'], 'id')
    require(before_auth.keys() <= after_auth.keys(), 'no original auth removal')
    revocation = {'revoked', 'revoked_at', 'revoke_reason'}
    for identity, row in before_auth.items():
        now = after_auth[identity]
        if row == now:
            continue
        require(row['user_id'] == owner and row['revoked'] is False and without(row, revocation) == without(now, revocation) and now['revoked'] is True and now['revoke_reason'] == 'REPLACED', 'only prior owner replaced')
        bounded(now['revoked_at'])
    fresh = [row for identity, row in after_auth.items() if identity not in before_auth]
    require(len(fresh) == 3 and collections.Counter(row['revoke_reason'] for row in fresh) == {'REPLACED': 1, 'LOGOUT': 2}, 'DIF016 three fresh session terminal reasons')
    require(all(row['user_id'] == owner and row['revoked'] is True for row in fresh), 'all fresh owned sessions revoked')
    for row in fresh:
        bounded(row['issued_at']); bounded(row['last_accessed_at']); bounded(row['revoked_at'])
    addresses = {row['client_address'] for row in fresh}
    require(len(addresses) == 1, 'one actual verified client address')
    before_ip = indexed(old['schubert.login_ip_attempts'], 'client_address')
    after_ip = indexed(new['schubert.login_ip_attempts'], 'client_address')
    require(before_ip.keys() <= after_ip.keys(), 'IP rows not deleted')
    for address, row in after_ip.items():
        if address not in addresses:
            require(before_ip.get(address) == row, 'other IP unchanged')
        else:
            require(row['failed_count'] == 0 and row['locked_until'] is None, 'successful client IP counters')
    inbox = added['schubert.request_inbox']
    counts = collections.Counter(row['request_layout_id'] for row in inbox)
    require(counts['LGNREQ01'] == 3 and counts['QSBREQ01'] == 1 and counts['LOGREQ01'] in {2, 3} and set(counts) <= {'LGNREQ01', 'QSBREQ01', 'LOGREQ01'}, 'only explicit update Inbox layouts; invalid-session revoke optional coordination')
    for row in inbox:
        require(row['processing_state'] == 'COMPLETED' and row['completed_at'] is not None and row['response_body_encrypted'] is not None, 'committed bounded Inbox')
        require(row['owner_user_id'] == (None if row['request_layout_id'] == 'LGNREQ01' else owner), 'Inbox owner')
        require(row['operation_token'] == (token if row['request_layout_id'] == 'QSBREQ01' else None), 'one retained operation')
        bounded(row['created_at']); bounded(row['completed_at'])
    mq = added['schubert.mq_outbox']
    require(len(mq) == 1 and mq[0]['destination'] == 'nk.async.work' and mq[0]['layout_id'] == 'QWKREQ01' and mq[0]['message_id'] == job['message_id'] and mq[0]['correlation_id'] == job['correlation_id'] and mq[0]['status'] == 'SENT' and mq[0]['lease_owner'] is mq[0]['lease_until'] is None, 'one actually sent internal job event')
    web = added['schubert_web_session.web_http_sessions']
    require(len(web) == 3 and all(row['max_inactive_seconds'] == 28800 for row in web), 'three post-logout anonymous sessions, eight-hour idle')
    for row in web:
        bounded(row['created_at']); bounded(row['last_accessed_at'])
    logs = added['schubert.app_logs']
    outbox = added['schubert_web_session.web_log_outbox']
    require(logs and outbox, 'actual audit delivery')
    sent = set()
    correlations = {}
    for row in outbox:
        require(row['layout_id'] == 'WLGEVT01' and row['layout_version'] == '001' and row['status'] == 'SENT' and row['lease_owner'] is row['lease_until'] is row['last_error_code'] is None, 'Web log delivery settled')
        require(type(row['correlation_id']) is str and row['message_id'] not in sent, 'unique log event identity')
        correlations[row['message_id']] = row['correlation_id']
        sent.add(row['message_id']); bounded(row['created_at']); bounded(row['sent_at'])
    observed = set()
    for row in logs:
        require(row['service'] in {'WEB', 'API'} and row['category'] in {'REQUEST', 'ACTION', 'SECURITY', 'MQ', 'SYSTEM'} and (row['level'] in {'INFO', 'WARN'} or row['level'] == 'ERROR' and row.get('action') == 'QUESTION_FAILED' and job['state'] == 'ERROR'), 'finite cohort audit scope')
        require(row['actor_user_id'] in {None, owner}, 'audit actor scope')
        bounded(row['logged_at'])
        if row['source_message_id'] is not None:
            # SS351: correlation is the first business message ID when one exists,
            # not necessarily this HTTP terminal event's own message ID.
            require(row['service'] == 'WEB' and row['source_message_id'] == row['message_id'] and row['source_message_id'] not in observed and correlations.get(row['source_message_id']) == row['correlation_id'], 'delivered Web audit identity and business correlation')
            observed.add(row['source_message_id'])
    require(observed == sent, 'Web audit/outbox exact one-to-one')
    return {'all24Qualified': True, 'newQuestions': 1, 'freshAuthSessions': 3, 'newJobs': 1, 'newNotifications': 1, 'newWebSessions': len(web), 'newInbox': len(inbox), 'newSentWebLogs': len(outbox), 'allPreviousProtectedRowsUnchanged': True, 'formalAccepted': False, 'answerProviderAcceptance': False, 'rawExported': False}


def main():
    import sys
    if len(sys.argv) != 4:
        raise ValueError('private before/after/context required')
    before, after, context = [json.loads(Path(name).read_bytes()) for name in sys.argv[1:]]
    print(json.dumps(qualify(before, after, context['owner'], context['lower'], context['upper']), sort_keys=True))


if __name__ == '__main__':
    main()
