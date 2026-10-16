"""Independent diagnostic guard fixtures, never Production PT/parent acceptance."""
import ast
import copy
import ipaddress
import unittest
from pathlib import Path
import pg4058_original_read_profile as profile


def guards(tcp, sockets, raw=None):
    tree = ast.parse(profile.RUN if raw is None else raw)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and n.name in {'peers', 'same_values', 'endpoint', 'tcp_pair'}]
    class FixedPath:
        def __init__(self, value, *parts):
            self.name = str(Path(value, *parts))
            if self.name not in {'/proc/net/tcp', '/proc/net/tcp6'}: raise ValueError('unexpected fixture file')
        def read_text(self):
            return tcp.get(self.name, 'header') if isinstance(tcp, dict) else tcp
    def require(v):
        if not v: raise ValueError('fixture guard refused')
    ns = {'Path': FixedPath, 'require': require, 'inodes': lambda pid: sockets.get(pid, set()), 'ipaddress': ipaddress}
    exec(compile(ast.Module(body=functions, type_ignores=[]), '<independent guards>', 'exec'), ns)
    return ns


class GuardTest(unittest.TestCase):
    def fixture(self, own):
        ordinary = [(220, 'schubert_app', 120, 6000), (221, 'schubert_app', 120, 6001),
                    (230, 'schubert_web_session', 130, 6002)]
        entries = ordinary + ([(240, 'schubert_batch', 140, 6003)] if own else [])
        tcp = ['header']; sockets = {}; rows = []
        for i, (backend, role, actor, port) in enumerate(entries):
            c, s = str(100 + i * 2), str(101 + i * 2)
            tcp.extend([f'0: 0100007F:{port:04X} 0100007F:1538 01 0 0 0 0 0 {c}',
                        f'0: 0100007F:1538 0100007F:{port:04X} 01 0 0 0 0 0 {s}'])
            sockets.setdefault(actor, set()).add(c); sockets.setdefault(backend, set()).add(s)
            rows.append({'pid': backend, 'user': role, 'application': 'PG286-original-profile'
                         if role == 'schubert_batch' else 'ordinary', 'address': '127.0.0.1', 'port': port})
        value = {'database': {'peers': rows, 'locks': [{'pid': 240, 'classid': 0, 'objid': 71419602,
                  'objsubid': 1, 'mode': 'ExclusiveLock', 'granted': True}] if own else []},
                 'actors': {'schubert-nk-api.service': {'pid': 120}, 'schubert-nk-web.service': {'pid': 130}},
                 'flocks': ['1: FLOCK ADVISORY WRITE 140 fixed 0 EOF',
                            '2: FLOCK ADVISORY WRITE 140 fixed2 0 EOF'] if own else []}
        return value, guards('\n'.join(tcp), sockets), sockets

    def test_live_pools_and_actual_owner_both_ends(self):
        for own in [False, True]:
            v, ns, sockets = self.fixture(own); owner = (140, 240) if own else None
            ns['peers'](v, owner)
            sockets[120].clear()
            with self.assertRaises(ValueError): ns['peers'](v, owner)

    def test_foreign_missing_duplicate_advisory_and_flock_refused(self):
        for key in ['role', 'extra', 'missing', 'advisory', 'flock', 'address', 'backend_socket']:
            v, ns, sockets = self.fixture(True)
            if key == 'role': v['database']['peers'][0]['user'] = 'schubert_migration'
            elif key == 'extra': v['database']['peers'].append(copy.deepcopy(v['database']['peers'][0]))
            elif key == 'missing': v['database']['peers'].pop(0)
            elif key == 'advisory': v['database']['locks'][0]['pid'] = 999
            elif key == 'flock': v['flocks'][0] = '1: FLOCK ADVISORY WRITE 999 fixed 0 EOF'
            elif key == 'address': v['database']['peers'][0]['address'] = '192.0.2.1'
            else: sockets[240].clear()
            with self.subTest(key=key), self.assertRaises(ValueError): ns['peers'](v, (140, 240))

    def test_every_preserved_category_and_rows(self):
        ns = guards('header', {})
        v = {k: {'fixed': 1} for k in ['units', 'actors', 'durable', 'native', 'startup', 'runtime']}
        v['database'] = {'rows': {'schubert.fixed': [{'value': 'independent'}]}}
        ns['same_values'](v, copy.deepcopy(v))
        for key in v:
            changed = copy.deepcopy(v)
            if key == 'database': changed[key]['rows']['schubert.fixed'][0]['value'] = 'tampered'
            else: changed[key]['fixed'] = 2
            with self.subTest(key=key), self.assertRaises(ValueError): ns['same_values'](v, changed)

    def test_fixed_source_and_no_mutating_mode(self):
        for action in ['compile', 'run']:
            raw = profile.payload(action); compile(raw, '<closed profile>', 'exec')
            self.assertFalse('systemctl stop' in raw or 'signal.SIGKILL' in raw or 'kill(' in raw,
                             'diagnostic must not issue actor signals')
            self.assertTrue('begin isolation level repeatable read read only' in raw,
                            'observer SQL must remain read-only')
        with self.assertRaises(ValueError): profile.payload('stop')
        java = (Path(profile.ROOT) / 'tools/quality/RootOriginalReadProfile.java').read_text()
        self.assertIn('MaintenanceFileLock.create().tryExclusive', java)
        self.assertIn('StartupAdmissionFile.create().tryExclusive', java)
        self.assertIn('db.setReadOnly(true); db.setAutoCommit(false)', java)
        self.assertIn('session.observeStartup(ORIGINAL)', java)
        self.assertIn('read-only profile never writes originals', java)


if __name__ == '__main__': unittest.main()
