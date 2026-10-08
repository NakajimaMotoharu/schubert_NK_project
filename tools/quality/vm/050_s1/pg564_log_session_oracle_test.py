"""Literal UI offset fixtures/independent AESGCM; no Production-generated expected values."""
import copy
import json
import struct
import unittest
import uuid
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pg564_log_session_oracle import verify, decrypt, log_aad, session_aad, anonymous_session


class Test(unittest.TestCase):
    def setUp(self):
        self.key = bytes(range(32))
        self.session_key = bytes(range(32, 64))
        mid = '00000000-0000-4000-8000-000000000001'
        rid = '00000000-0000-4000-8000-000000000002'
        sid = '00000000-0000-4000-8000-000000000003'
        self.when = '2026-10-08T04:25:00.123000Z'
        detail = {'responseBytes': 1024, 'projectionStatus': 'PENDING'}
        self.log = dict(id=1, action='HTTP_REQUEST_COMPLETED', category='REQUEST', level='INFO',
                        service='WEB', message='HTTP request completed', http_method='GET',
                        request_uri='/login', status_code=200, actor_user_id=None, actor_username=None,
                        security_hold_until=None, duration_ms=12, remote_address='127.0.0.1',
                        request_id=rid, message_id=mid, source_message_id=mid, correlation_id=mid,
                        logged_at=self.when, details=detail)
        self.local = dict(timestamp=self.when, service='WEB', appVersion='0.1.0-SNAPSHOT',
                          configVersion='PG548', category='REQUEST', level='INFO',
                          action='HTTP_REQUEST_COMPLETED', outcome='SUCCESS', messageId=mid,
                          correlationId=mid, requestId=rid, message='HTTP request completed',
                          httpMethod='GET', path='/login', status=200, elapsedMs=12,
                          remoteAddress='127.0.0.1', details=detail)
        self.outbox = dict(id=1, message_id=mid, correlation_id=mid, key_version='v1',
                           layout_id='WLGEVT01', layout_version='001', status='SENT', attempt_count=0,
                           lease_owner=None, lease_until=None, last_error_code=None, created_at=self.when,
                           next_attempt_at=self.when, sent_at='2026-10-08T04:25:01.000000Z')
        header = bytearray(b' ' * 256)
        for offset, literal in [(0, b'SCHBNK01'), (8, b'001'), (11, b'WLGEVT01'), (19, b'001'),
                                (22, b'EI'), (24, mid.encode()), (60, mid.encode()),
                                (96, b'20261008132500123'), (177, b'0256'), (181, b'002080'),
                                (187, b'000000'), (193, b'000000'), (199, b'000002336')]:
            header[offset:offset + len(literal)] = literal
        data = bytearray(b' ' * 2080)
        for offset, text in [(0, '20261008132500123'), (17, 'REQUEST'), (33, 'INFO'),
                             (41, 'HTTP_REQUEST_COMPLETED'), (105, 'HTTP request completed'),
                             (617, rid), (653, 'GET'), (661, '/login'), (917, '200'), (920, '12'),
                             (929, '127.0.0.1'), (1043, json.dumps(detail, separators=(',', ':')))]:
            raw = text.encode(); data[offset:offset + len(raw)] = raw
        self.wire = bytes(header + data)
        # AAD literal construction independent of the oracle AAD functions.
        parts = [b'web-log-outbox', b'schubert_web_session.web_log_outbox', uuid.UUID(mid).bytes,
                 uuid.UUID(mid).bytes, b'\1', b'v1', b'WLGEVT01', b'001']
        self.log_aad = b''.join(struct.pack('>I', len(p)) + p for p in parts)
        self.outbox['payload_ciphertext'] = self.encrypt(self.wire, self.key, self.log_aad)
        self.session = dict(id=sid, session_id_hash='a' * 64, key_version='v1', created_at=self.when,
                            last_accessed_at=self.when, expires_at='2026-10-08T12:25:00.123000Z',
                            max_inactive_seconds=28800, version=3)
        seconds = 1791433500
        parts = [b'web-session', b'schubert_web_session.web_http_sessions', uuid.UUID(sid).bytes,
                 b'a' * 64, struct.pack('>qI', seconds, 123000000), b'\1', b'v1']
        self.session_aad = b''.join(struct.pack('>I', len(p)) + p for p in parts)
        self.attrs = b'{"formatVersion":2,"csrfToken":"' + b'c' * 64 + b'","operationTokens":[]}'
        self.session['attributes_ciphertext'] = self.encrypt(self.attrs, self.session_key, self.session_aad)
        self.old = {'schubert.app_logs': [], 'schubert_web_session.web_log_outbox': [],
                    'schubert_web_session.web_http_sessions': []}
        self.new = {'schubert.app_logs': [self.log], 'schubert_web_session.web_log_outbox': [self.outbox],
                    'schubert_web_session.web_http_sessions': [self.session]}

    @staticmethod
    def encrypt(raw, key, aad):
        nonce = bytes(range(12))
        return '\\x' + (b'NKENC1\1\2v1' + nonce + AESGCM(key).encrypt(nonce, raw, aad)).hex()

    def test_literal_wire_json_aad_success(self):
        self.assertEqual(log_aad(self.outbox), self.log_aad)
        self.assertEqual(session_aad(self.session), self.session_aad)
        result = verify(self.old, self.new, [self.local], self.key, self.session_key, 1)
        self.assertEqual(result['logWireDbLocalVerified'], 1)
        self.assertEqual(result['anonymousSessionEncryptedVerified'], 1)
        self.assertFalse(result['wholeFormalAccepted'])

    def test_tag_key_version_transplant_envelope_rejection(self):
        raw = self.outbox['payload_ciphertext']
        cases = [(raw[:-2] + '00', 'v1', self.key, self.log_aad, 2336),
                 (raw, 'v2', self.key, self.log_aad, 2336),
                 (raw, 'v1', self.session_key, self.log_aad, 2336),
                 (raw, 'v1', self.key, self.session_aad, 2336),
                 (raw, 'v1', self.key, self.log_aad, 2335),
                 ('\\x00', 'v1', self.key, self.log_aad, 2336)]
        for args in cases:
            with self.assertRaises((ValueError, InvalidTag)): decrypt(*args)

    def test_projection_fields_counts_null_duplicate_and_old_preservation(self):
        for table, field, value in [('schubert.app_logs', 'duration_ms', True),
                                    ('schubert.app_logs', 'request_uri', '/other'),
                                    ('schubert.app_logs', 'actor_user_id', 1),
                                    ('schubert_web_session.web_log_outbox', 'status', 'ERROR'),
                                    ('schubert_web_session.web_log_outbox', 'lease_owner', 'held'),
                                    ('schubert_web_session.web_http_sessions', 'expires_at', self.when)]:
            bad = copy.deepcopy(self.new); bad[table][0][field] = value
            with self.assertRaises(ValueError): verify(self.old, bad, [self.local], self.key, self.session_key, 1)
        for events in ([], [self.local, self.local], [dict(self.local, status=None)]):
            with self.assertRaises(ValueError): verify(self.old, self.new, events, self.key, self.session_key, 1)
        for table in self.new:
            bad = copy.deepcopy(self.new); bad[table].append(copy.deepcopy(bad[table][0]))
            with self.assertRaises(ValueError): verify(self.old, bad, [self.local], self.key, self.session_key, 1)
        old = copy.deepcopy(self.old); old['schubert.app_logs'] = [dict(self.log, message='old')]
        with self.assertRaises(ValueError): verify(old, self.new, [self.local], self.key, self.session_key, 1)

    def test_closed_anonymous_json_and_session_metadata(self):
        for raw in (b'null', b'{}', self.attrs.replace(b':2,', b':true,'),
                    self.attrs.replace(b'"operationTokens":[]', b'"operationTokens":null'),
                    self.attrs.replace(b'"formatVersion":2', b'"formatVersion":2,"username":"u"'),
                    self.attrs.replace(b'"formatVersion":2', b'"formatVersion":2,"formatVersion":2'),
                    b'\xef\xbb\xbf' + self.attrs, self.attrs + b'{}'):
            with self.assertRaises(ValueError): anonymous_session(self.session, bytearray(raw))
        for field, value in [('version', True), ('max_inactive_seconds', 0), ('created_at', None)]:
            with self.assertRaises(ValueError): anonymous_session(dict(self.session, **{field: value}), bytearray(self.attrs))


if __name__ == '__main__':
    unittest.main()
