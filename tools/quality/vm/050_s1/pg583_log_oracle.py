"""Independent current cohort: 116 login GET + one normalized CSS GET, 116 sessions."""
from collections import Counter
from pg564_log_session_oracle import require, decrypt, log_aad, session_aad, anonymous_session, event_wire


def verify(old, current, events, log_key, session_key, expected_groups=None, expected_sessions=116):
    if expected_groups is None:
        expected_groups = {('/login', 'GET', 200): 116, ('/css/**', 'GET', 200): 1}
    require(type(events) is list and type(expected_sessions) is int and expected_sessions > 0)
    count = sum(expected_groups.values())
    added = {}
    for table in ('schubert.app_logs', 'schubert_web_session.web_log_outbox', 'schubert_web_session.web_http_sessions'):
        prior = {r['id']: r for r in old[table]}
        now = {r['id']: r for r in current[table]}
        require(len(prior) == len(old[table]) and len(now) == len(current[table])
                and all(now.get(k) == v for k, v in prior.items()))
        added[table] = [r for k, r in now.items() if k not in prior]
    logs = {r['source_message_id']: r for r in added['schubert.app_logs']}
    local = {r['messageId']: r for r in events}
    outbox = added['schubert_web_session.web_log_outbox']
    require(len(logs) == len(added['schubert.app_logs']) == len(local) == len(events) == len(outbox) == count
            and set(logs) == set(local) == {r['message_id'] for r in outbox})
    require(Counter((r['request_uri'], r['http_method'], r['status_code']) for r in logs.values()) == expected_groups)
    nonces = set()
    for row in outbox:
        require(row['key_version'] == 'v1')
        wire, nonce = decrypt(row['payload_ciphertext'], row['key_version'], log_key, log_aad(row), 2336)
        try:
            require(nonce not in nonces)
            nonces.add(nonce)
            log = logs[row['message_id']]
            event_wire(row, wire, log, local[row['message_id']], expected_path=log['request_uri'])
        finally:
            wire[:] = b'\0' * len(wire)
    sessions = added['schubert_web_session.web_http_sessions']
    require(len(sessions) == len({r['session_id_hash'] for r in sessions}) == expected_sessions)
    nonces = set()
    for row in sessions:
        require(row['key_version'] == 'v1')
        plaintext, nonce = decrypt(row['attributes_ciphertext'], row['key_version'], session_key, session_aad(row), 16384)
        try:
            require(nonce not in nonces)
            nonces.add(nonce)
            anonymous_session(row, plaintext)
        finally:
            plaintext[:] = b'\0' * len(plaintext)
    return {'actualExit': 0, 'logWireDbLocalVerified': count, 'outboxSentVerified': count,
            'anonymousSessionEncryptedVerified': expected_sessions, 'expectedHttpGroupsVerified': True,
            'oldAllThreeTablesFullRowsProtected': True, 'duplicateMessageNonceSession0': True,
            'plaintextExported': False, 'wholeFormalAccepted': False}
