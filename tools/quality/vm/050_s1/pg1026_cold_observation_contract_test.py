"""Independent literals and actual FS mutation; no guest, DB or signal actions."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from pg1026_cold_observation_contract import HeldInventory, all_client_sql, terminate_once, durable_reservation, fd_alias_records


class Contract(unittest.TestCase):
    def fixture(self):
        # Production requires non-group-writable ancestors. The repository has
        # group-writable parents, so it is not a valid trusted fixture namespace.
        temporary = tempfile.TemporaryDirectory(prefix='pg1026-test-', dir='/home/mini')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / 'payload').write_bytes(b'ABCD')
        (root / 'payload').chmod(0o600)
        return root, [{'path': 'payload', 'size': 4,
                       'sha256': 'e12e115acf4552b2568b55e93cbd39394c4ef81c82447fafc997882a02d23677'}]

    def test_actual_literal_inventory_and_normal_close(self):
        root, records = self.fixture()
        held = HeldInventory(str(root), records, os.getuid()).open()
        first = held.capture()
        self.assertEqual(first, held.capture())
        self.assertEqual(records[0]['sha256'], first[-1][3])
        self.assertEqual(os.getuid(), first[-1][1][2])
        held.close()
        with self.assertRaises(ValueError): held.capture()
        with self.assertRaises(ValueError): held.close()

    def test_actual_same_bytes_chmod_between_reads_rejected(self):
        root, records = self.fixture()
        held = HeldInventory(str(root), records, os.getuid()).open()
        self.addCleanup(held.close)
        (root / 'payload').chmod(0o400)
        self.assertEqual(records[0]['sha256'], hashlib.sha256((root / 'payload').read_bytes()).hexdigest())
        with self.assertRaises(ValueError): held.capture()

    def test_actual_inode_replace_and_xattr_rejected(self):
        for change in ('replace', 'xattr'):
            with self.subTest(change=change):
                root, records = self.fixture()
                held = HeldInventory(str(root), records, os.getuid()).open()
                try:
                    if change == 'replace':
                        (root / 'new').write_bytes(b'ABCD')
                        (root / 'new').chmod(0o600)
                        (root / 'new').replace(root / 'payload')
                    else:
                        os.setxattr(root / 'payload', 'user.pg1026', b'changed')
                    with self.assertRaises(ValueError): held.capture()
                finally: held.close()

    def test_actual_unsigned_extra_missing_symlink_and_wrong_bytes_rejected(self):
        for change in ('extra', 'missing', 'symlink', 'bytes'):
            with self.subTest(change=change):
                root, records = self.fixture()
                if change == 'extra': (root / 'extra').write_bytes(b'X')
                if change == 'missing': (root / 'payload').unlink()
                if change == 'symlink':
                    (root / 'payload').unlink()
                    (root / 'payload').symlink_to('/etc/hostname')
                if change == 'bytes': (root / 'payload').write_bytes(b'ABCE')
                with self.assertRaises((ValueError, OSError)):
                    HeldInventory(str(root), records, os.getuid()).open()

    def test_null_unknown_path_hash_owner_contract(self):
        root, records = self.fixture()
        for records_, owner in ((None, os.getuid()), ([], 0), (records, None), (records, True)):
            with self.assertRaises(ValueError): HeldInventory(str(root), records_, owner)
        for name in ('../payload', '/payload', 'a//b', '.', 'a\\b', 'a\n'):
            with self.assertRaises(ValueError):
                HeldInventory(str(root), [{**records[0], 'path': name}], os.getuid())

    def test_actual_nested_inventory_extra_and_group_write_rejected(self):
        root, records = self.fixture()
        (root / 'nested').mkdir(mode=0o700)
        (root / 'payload').replace(root / 'nested' / 'payload')
        records[0]['path'] = 'nested/payload'
        held = HeldInventory(str(root), records, os.getuid()).open()
        try:
            self.assertEqual(records[0]['sha256'], held.capture()[-1][3])
            (root / 'extra').mkdir(mode=0o700)
            with self.assertRaises(ValueError): held.capture()
        finally: held.close()
        (root / 'extra').rmdir()
        (root / 'nested').chmod(0o770)
        with self.assertRaises(ValueError): HeldInventory(str(root), records, os.getuid()).open()

    def test_actual_separate_material_scope_does_not_claim_directory_closure(self):
        root, records = self.fixture()
        (root / 'unrelated').write_bytes(b'not release inventory')
        held = HeldInventory(str(root), records, os.getuid()).open_file()
        try:
            self.assertEqual(records[0]['sha256'], held.capture()[-1][3])
            (root / 'payload').chmod(0o400)
            with self.assertRaises(ValueError): held.capture()
        finally: held.close()
        with self.assertRaises(ValueError): HeldInventory(str(root), records + [{**records[0], 'path':'other'}], os.getuid()).open_file()

    def test_actual_reservation_durable_exclusive_and_symlink_refused(self):
        root, _ = self.fixture()
        fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            literal = b'{"pid":121,"ticks":31}'
            durable_reservation(fd, '121.term-reserved.private.json', literal)
            self.assertEqual(literal, (root / '121.term-reserved.private.json').read_bytes())
            self.assertEqual(0o600, (root / '121.term-reserved.private.json').stat().st_mode & 0o777)
            with self.assertRaises(FileExistsError): durable_reservation(fd, '121.term-reserved.private.json', literal)
            (root / '122.term-reserved.private.json').symlink_to(root / 'payload')
            with self.assertRaises(FileExistsError): durable_reservation(fd, '122.term-reserved.private.json', literal)
            self.assertEqual(b'ABCD', (root / 'payload').read_bytes())
            for name, data in (('../123.term-reserved.private.json', literal), ('123.term-reserved.private.json', None), ('123.term-reserved.private.json', b'')):
                with self.assertRaises(ValueError): durable_reservation(fd, name, data)
        finally: os.close(fd)

    def test_actual_flock_fd_alias_and_literal_non_alias(self):
        import fcntl
        root, _ = self.fixture()
        fd = os.open(root / 'payload', os.O_RDONLY)
        duplicate = os.dup(fd)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            records = [line.removeprefix('lock:').strip() for n in (fd, duplicate)
                       for line in Path('/proc/self/fdinfo/' + str(n)).read_text().splitlines() if line.startswith('lock:')]
            self.assertEqual(2, len(records))
            self.assertEqual(1, len(fd_alias_records(records)))
        finally:
            os.close(duplicate)
            os.close(fd)
        self.assertEqual(['1: FLOCK ADVISORY WRITE 121 08:01:7 0 EOF', '1: FLOCK ADVISORY WRITE 122 08:01:7 0 EOF'],
                         fd_alias_records(['2: FLOCK ADVISORY WRITE 121 08:01:7 0 EOF', '1: FLOCK ADVISORY WRITE 121 08:01:7 0 EOF', '3: FLOCK ADVISORY WRITE 122 08:01:7 0 EOF']))
        for lines in (None, [None], ['1: -> FLOCK ADVISORY WRITE 121 08:01:7 0 EOF'], ['1: FLOCK ADVISORY READ 121 08:01:7 0 EOF']):
            with self.assertRaises(ValueError): fd_alias_records(lines)

    def test_all_roles_sql_independent_literal_and_rows(self):
        self.assertEqual("select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid()and pid<>121;", all_client_sql(121))
        rows = [('schubert_nk', 'client backend', 20, 'migration'),
                ('schubert_nk', 'client backend', 21, 'unknown'),
                ('schubert_nk', 'client backend', 121, 'schubert_batch'),
                ('schubert_nk', 'client backend', 122, 'observer'),
                ('other', 'client backend', 23, 'unknown')]
        self.assertEqual([20, 21], [r[2] for r in rows if r[0] == 'schubert_nk' and r[1] == 'client backend' and r[2] not in (121, 122)])
        self.assertNotIn('usename', all_client_sql(0))
        for pid in (None, True, -1, 1, '121', 2147483647):
            with self.assertRaises(ValueError): all_client_sql(pid)

    def test_once_term_order_and_post_reservation_recheck(self):
        calls = []
        def verify(pid, ticks): calls.append('verify'); return (pid, ticks)
        terminate_once(121, 31, verify, lambda *_: calls.append('reserve'),
                       lambda _: calls.append('open') or 7,
                       lambda _: calls.append('send'),
                       lambda _: calls.append('wait') or True,
                       lambda _: calls.append('close'))
        self.assertEqual(['verify', 'open', 'verify', 'reserve', 'verify', 'send', 'wait', 'close'], calls)
        calls.clear()
        counter = [0]
        def changed(*_):
            counter[0] += 1
            return counter[0] == 3
        with self.assertRaises(ValueError):
            terminate_once(121, 31, changed, lambda *_: calls.append('reserve'), lambda _: 7,
                           lambda _: calls.append('send'), lambda _: True, lambda _: calls.append('close'))
        self.assertEqual(['reserve', 'close'], calls)

    def test_unknown_send_timeout_and_close_never_retried(self):
        for fault in ('send', 'wait', 'close', 'send-close'):
            with self.subTest(fault=fault):
                calls = []
                error = OSError('independent injected fault')
                def send(_):
                    calls.append('send')
                    if fault in ('send', 'send-close'): raise error
                def close(_):
                    calls.append('close')
                    if fault in ('close', 'send-close'): raise RuntimeError('close unknown')
                with self.assertRaises((OSError, ValueError, RuntimeError)) as raised:
                    terminate_once(121, 31, lambda *_: 'fixed', lambda *_: calls.append('reserve'),
                                   lambda _: 7, send, lambda _: fault != 'wait', close)
                self.assertEqual(['reserve', 'send', 'close'], calls)
                if fault in ('send', 'send-close'): self.assertIs(error, raised.exception)


if __name__ == '__main__': unittest.main()
