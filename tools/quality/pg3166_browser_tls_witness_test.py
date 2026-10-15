"""Pure strict TLS delegation/listener/CA drift and certificate-failure propagation."""
import ast
import hashlib
import ssl
import types
import unittest
from unittest.mock import patch
from pg3140_browser_business_actual import TLS_WITNESS


class StrictTls(unittest.TestCase):
    def exercise(self, fault=None):
        state = {'reads': 0, 'listeners': 0, 'connects': 0}
        class File:
            def __init__(self, path):self.path = path
            def __truediv__(self, suffix):return File(self.path + '/' + str(suffix))
            def __str__(self):return self.path
            def iterdir(self):return [File(self.path + '/3')]
            def readlink(self):return 'socket:[55]'
            def read_text(self):
                state['listeners'] += 1
                inode = '56' if fault == 'listener' and state['listeners'] > 1 else '55'
                return 'header\n0: 0F02000A:D778 00000000:0000 0A 0 0 0 0 0 ' + inode + '\n'
            def lstat(self):return types.SimpleNamespace(st_dev=1, st_ino=2, st_uid=3, st_gid=3, st_mode=0o100600, st_nlink=1, st_size=4, st_mtime_ns=5, st_ctime_ns=6)
            def read_bytes(self):
                state['reads'] += 1
                return b'drift' if fault == 'ca' and state['reads'] > 1 else b'CERT'
        class Connection:
            def __enter__(self):return self
            def __exit__(self, *args):return False
            def version(self):return 'TLSv1' if fault == 'version' else 'TLSv1.3'
            def getpeercert(self, binary_form):return b'PEER' if binary_form else None
        class Context:
            check_hostname = fault != 'hostname-disabled'
            verify_mode = ssl.CERT_NONE if fault == 'verification-disabled' else ssl.CERT_REQUIRED
            def wrap_socket(self, connection, server_hostname):
                self_hostname = server_hostname
                if self_hostname != '10.0.2.15':raise AssertionError('fixed SAN target')
                if fault == 'certificate':raise ssl.SSLCertVerificationError('synthetic invalid cert')
                return Connection()
        def connect(address, timeout):
            self.assertEqual(('10.0.2.15', 55160), address); self.assertEqual(3, timeout)
            state['connects'] += 1; return Connection()
        def require(value):
            if not value:raise ValueError('strict TLS boundary refused')
        fn = next(node for node in ast.parse(TLS_WITNESS).body if isinstance(node, ast.FunctionDef))
        ns = {'pathlib': types.SimpleNamespace(Path=File), 'EXPECTED': {'caddy.service': ['123']}, 'require': require, 'hashlib': hashlib, 'os': types.SimpleNamespace(listxattr=lambda path: [])}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), '<pure normal TLS witness>', 'exec'), ns)
        with patch('ssl.create_default_context', return_value=Context()) as create, patch('socket.create_connection', side_effect=connect):
            result = ns['independent_tls_peer']()
            create.assert_called_once_with(cafile='/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt')
        self.assertEqual(1, state['connects'])
        return result

    def test_strict_default_context_and_fixed_owned_listener_without_http(self):
        result = self.exercise()
        self.assertTrue(result['normalChainAndIpSanValidated'] and result['sameOwnedCaddyListener'])
        self.assertEqual(0, result['httpRequestsSent'])

    def test_every_invalid_trust_or_drift_propagates_as_failure(self):
        for fault in ['listener', 'ca', 'version', 'hostname-disabled', 'verification-disabled', 'certificate']:
            with self.assertRaises((ValueError, ssl.SSLCertVerificationError)):
                self.exercise(fault)


if __name__ == '__main__':
    unittest.main()
