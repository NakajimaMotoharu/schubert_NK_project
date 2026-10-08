"""Independent UI232/235, SS314/324/351/352 oracle for PG554 anonymous login GETs.

Uses Python AESGCM, literal offsets, closed JSON and DB postconditions, never Java
Production codecs. All decrypted data stays inside the private collector process.
Trace: FUN-008/MON-003/AUT-001; PT-OPS-PG564-001..006; WBS-N15.04.
"""
import datetime
import ipaddress
import json
import re
import struct
import uuid
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def require(condition):
    if not condition:
        raise ValueError('independent log/session oracle refused')


def instant(value):
    require(type(value) is str)
    result = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(result.tzinfo is not None)
    return result


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result)
        result[key] = value
    return result


def closed_json(raw):
    require(type(raw) in (bytes, bytearray) and not raw.startswith(b'\xef\xbb\xbf'))
    return json.loads(bytes(raw).decode('utf-8'), object_pairs_hook=unique)


def identifier(value):
    require(type(value) is str)
    parsed = uuid.UUID(value)
    require(str(parsed) == value and parsed.int != 0)
    return parsed.bytes


def prefix(fields):
    return b''.join(struct.pack('>I', len(p)) + p for p in fields)


def log_aad(row):
    return prefix([b'web-log-outbox', b'schubert_web_session.web_log_outbox',
                   identifier(row['message_id']), identifier(row['correlation_id']),
                   b'\x01', row['key_version'].encode('ascii'), b'WLGEVT01', b'001'])


def session_aad(row):
    created = instant(row['created_at'])
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    seconds = (created - epoch).days * 86400 + (created - epoch).seconds
    require(re.fullmatch('[0-9a-f]{64}', row['session_id_hash']) is not None)
    return prefix([b'web-session', b'schubert_web_session.web_http_sessions',
                   identifier(row['id']), row['session_id_hash'].encode('ascii'),
                   struct.pack('>qI', seconds, created.microsecond * 1000),
                   b'\x01', row['key_version'].encode('ascii')])


def decrypt(encoded, version, key, aad, maximum):
    require(type(encoded) is str and encoded.startswith('\\x') and type(version) is str)
    raw = bytes.fromhex(encoded[2:])
    require(re.fullmatch('[A-Za-z0-9][A-Za-z0-9._-]{0,15}', version) is not None)
    require(len(key) == 32 and len(raw) >= 37 and raw[:7] == b'NKENC1\x01')
    size = raw[7]
    require(1 <= size <= 16 and len(raw) >= 8 + size + 28)
    require(raw[8:8 + size] == version.encode('ascii'))
    offset = 8 + size
    require(len(raw) - offset - 28 <= maximum)
    nonce = raw[offset:offset + 12]
    plaintext = bytearray(AESGCM(key).decrypt(nonce, raw[offset + 12:], aad))
    require(0 < len(plaintext) <= maximum)
    return plaintext, nonce


def event_wire(outbox, wire, log, local):
    require(len(wire) == 2336)
    stamp = instant(log['logged_at']).astimezone(datetime.timezone(datetime.timedelta(hours=9)))
    jst = (stamp.strftime('%Y%m%d%H%M%S') + f'{stamp.microsecond // 1000:03}').encode('ascii')
    header = (b'SCHBNK01001WLGEVT01001EI' + outbox['message_id'].encode('ascii')
              + outbox['correlation_id'].encode('ascii') + jst + b' ' * 64
              + b'0256002080000000000000000002336' + b' ' * 48)
    require(len(header) == 256 and wire[:256] == header)
    data = wire[256:]
    require(data[:17] == jst and data[2067:] == b' ' * 13)
    expected = [(17, 16, 'REQUEST'), (33, 8, 'INFO'), (41, 64, 'HTTP_REQUEST_COMPLETED'),
                (105, 512, 'HTTP request completed'), (617, 36, log['request_id']),
                (653, 8, 'GET'), (661, 256, '/login'), (917, 3, '200'),
                (920, 9, str(log['duration_ms'])), (929, 45, log['remote_address']),
                (974, 64, ''), (1038, 5, '')]
    for start, length, value in expected:
        encoded = value.encode('utf-8')
        require(len(encoded) <= length and data[start:start + length] == encoded.ljust(length, b' '))
    details = closed_json(bytearray(data[1043:2067].rstrip(b' ')))
    require(type(details) is dict and set(details) == {'projectionStatus', 'responseBytes'})
    require(details['projectionStatus'] == 'PENDING' and type(details['responseBytes']) is int
            and 0 < details['responseBytes'] <= 999999999999)
    require(log['details'] == details == local['details'])
    require(log['action'] == 'HTTP_REQUEST_COMPLETED' and log['category'] == 'REQUEST'
            and log['level'] == 'INFO' and log['service'] == 'WEB'
            and log['message'] == 'HTTP request completed' and log['http_method'] == 'GET'
            and log['request_uri'] == '/login' and type(log['status_code']) is int
            and log['status_code'] == 200 and log['actor_user_id'] is None
            and log['actor_username'] is None and log['security_hold_until'] is None)
    require(type(log['duration_ms']) is int and 0 <= log['duration_ms'] <= 999999999)
    require(str(ipaddress.ip_address(log['remote_address'])) == log['remote_address'])
    require(outbox['message_id'] == outbox['correlation_id'] == log['message_id']
            == log['source_message_id'] == log['correlation_id'])
    require(outbox['layout_id'] == 'WLGEVT01' and outbox['layout_version'] == '001'
            and outbox['status'] == 'SENT' and type(outbox['attempt_count']) is int
            and outbox['attempt_count'] == 0 and outbox['lease_owner'] is None
            and outbox['lease_until'] is None and outbox['last_error_code'] is None)
    require(instant(outbox['created_at']) == instant(log['logged_at'])
            and instant(outbox['next_attempt_at']) == instant(outbox['created_at'])
            and instant(outbox['sent_at']) >= instant(outbox['created_at']))
    expected_local = {'timestamp', 'service', 'appVersion', 'configVersion', 'level', 'category',
                      'action', 'outcome', 'messageId', 'correlationId', 'requestId', 'message',
                      'httpMethod', 'path', 'status', 'elapsedMs', 'remoteAddress', 'details'}
    require(type(local) is dict and set(local) == expected_local)
    require(instant(local['timestamp']) == instant(log['logged_at'])
            and local['service'] == 'WEB' and local['level'] == 'INFO'
            and local['category'] == 'REQUEST' and local['action'] == log['action']
            and local['outcome'] == 'SUCCESS' and local['message'] == log['message']
            and local['messageId'] == outbox['message_id']
            and local['correlationId'] == outbox['correlation_id']
            and local['requestId'] == log['request_id'] and local['httpMethod'] == 'GET'
            and local['path'] == '/login' and type(local['status']) is int
            and local['status'] == 200 and type(local['elapsedMs']) is int
            and local['elapsedMs'] == log['duration_ms']
            and local['remoteAddress'] == log['remote_address'])
    require(type(local['appVersion']) is str and 0 < len(local['appVersion'].encode()) <= 64
            and type(local['configVersion']) is str and 0 < len(local['configVersion'].encode()) <= 64)


def anonymous_session(row, plaintext):
    value = closed_json(plaintext)
    require(type(value) is dict and list(value) == ['formatVersion', 'csrfToken', 'operationTokens'])
    require(type(value['formatVersion']) is int and value['formatVersion'] == 2
            and type(value['csrfToken']) is str and re.fullmatch('[0-9a-f]{64}', value['csrfToken'])
            is not None and type(value['operationTokens']) is list and value['operationTokens'] == [])
    require(type(row['version']) is int and 0 <= row['version'] <= 999999999
            and type(row['max_inactive_seconds']) is int and row['max_inactive_seconds'] == 28800)
    require(instant(row['created_at']) <= instant(row['last_accessed_at'])
            and instant(row['expires_at']) == instant(row['last_accessed_at']) + datetime.timedelta(hours=8))


def verify(old, current, events, log_key, session_key, count=114):
    require(type(count) is int and count > 0 and type(events) is list)
    added = {}
    for table in ('schubert.app_logs', 'schubert_web_session.web_log_outbox',
                  'schubert_web_session.web_http_sessions'):
        prior = {r['id']: r for r in old[table]}
        now = {r['id']: r for r in current[table]}
        require(len(prior) == len(old[table]) and len(now) == len(current[table]))
        # Session rows removed by the independently verified Cleanup are not recreated.
        if table != 'schubert_web_session.web_http_sessions':
            require(all(now.get(k) == v for k, v in prior.items()))
        added[table] = [r for k, r in now.items() if k not in prior]
        require(len(added[table]) == count)
    logs = {r['source_message_id']: r for r in added['schubert.app_logs']}
    local = {e['messageId']: e for e in events}
    outbox = added['schubert_web_session.web_log_outbox']
    require(len(logs) == len(local) == len(events) == count
            and set(logs) == set(local) == {r['message_id'] for r in outbox})
    nonces = set()
    for row in outbox:
        require(row['key_version'] == 'v1')
        wire, nonce = decrypt(row['payload_ciphertext'], row['key_version'], log_key, log_aad(row), 2336)
        try:
            require(nonce not in nonces)
            nonces.add(nonce)
            event_wire(row, wire, logs[row['message_id']], local[row['message_id']])
        finally:
            wire[:] = b'\x00' * len(wire)
    sessions = added['schubert_web_session.web_http_sessions']
    require(len({r['session_id_hash'] for r in sessions}) == count)
    nonces = set()
    for row in sessions:
        require(row['key_version'] == 'v1')
        plaintext, nonce = decrypt(row['attributes_ciphertext'], row['key_version'], session_key,
                                   session_aad(row), 16384)
        try:
            require(nonce not in nonces)
            nonces.add(nonce)
            anonymous_session(row, plaintext)
        finally:
            plaintext[:] = b'\x00' * len(plaintext)
    return {'logWireDbLocalVerified': count, 'outboxSentVerified': count,
            'anonymousSessionEncryptedVerified': count, 'duplicateMessageNonceSession0': True,
            'plaintextExported': False, 'wholeFormalAccepted': False, 'actualExit': 0}
