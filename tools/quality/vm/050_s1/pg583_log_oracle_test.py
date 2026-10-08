"""Independent UI235 fixed offset/path fixture plus exact separate session count."""
import copy
import unittest
from pg564_log_session_oracle_test import Test as PriorVectors
from pg583_log_oracle import verify


class Test(unittest.TestCase):
    def test_login_and_css_closed_paths(self):
        prior = PriorVectors()
        prior.setUp()
        for path in ('/login', '/css/**'):
            wire = bytearray(prior.wire)
            wire[917:1173] = path.encode().ljust(256, b' ')
            current = copy.deepcopy(prior.new)
            current['schubert.app_logs'][0]['request_uri'] = path
            current['schubert_web_session.web_log_outbox'][0]['payload_ciphertext'] = prior.encrypt(bytes(wire), prior.key, prior.log_aad)
            local = dict(prior.local, path=path)
            result = verify(prior.old, current, [local], prior.key, prior.session_key, {(path, 'GET', 200): 1}, 1)
            self.assertEqual(1, result['outboxSentVerified'])
            self.assertEqual(1, result['anonymousSessionEncryptedVerified'])
            for expected in ({('/unknown', 'GET', 200): 1}, {(path, 'GET', 404): 1}):
                with self.assertRaises(ValueError):
                    verify(prior.old, current, [local], prior.key, prior.session_key, expected, 1)
            with self.assertRaises(ValueError):
                verify(prior.old, current, [local], prior.key, prior.session_key, {(path, 'GET', 200): 1}, 2)

    def test_protected_old_session_and_request_count(self):
        prior = PriorVectors()
        prior.setUp()
        for events in ([], [prior.local, prior.local]):
            with self.assertRaises(ValueError):
                verify(prior.old, prior.new, events, prior.key, prior.session_key, {('/login', 'GET', 200): 1}, 1)
        old = copy.deepcopy(prior.old)
        old['schubert_web_session.web_http_sessions'] = [dict(prior.session, version=99)]
        with self.assertRaises(ValueError):
            verify(old, prior.new, [prior.local], prior.key, prior.session_key, {('/login', 'GET', 200): 1}, 1)


if __name__ == '__main__':
    unittest.main()
