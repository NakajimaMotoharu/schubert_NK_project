"""Independent synthetic child and real O_EXCL/NOFOLLOW metadata oracle."""
import os
import pathlib
import stat
import sys
import tempfile
from pg471_private_command import run

checks = 0


def check(value):
    global checks
    checks += 1
    assert value


with tempfile.TemporaryDirectory(prefix='pg471-private-log-') as name:
    root = pathlib.Path(name)
    prior = os.umask(0)
    try:
        p = root / 'vector.private.log'
        check(run(p, [sys.executable, '-c', 'import sys; print("literal out"); print("literal err",file=sys.stderr); sys.exit(7)']) == 7)
        check(stat.S_IMODE(p.stat().st_mode) == 0o600)
        check(sorted(p.read_bytes().splitlines()) == [b'literal err', b'literal out'])
        original = p.read_bytes()
        inode = p.stat().st_ino
        link = root / 'link.private.log'; link.symlink_to(p)
        directory = root / 'directory.private.log'; directory.mkdir(mode=0o700)
        for target in (p, link, directory):
            try:
                run(target, [sys.executable, '-c', 'raise SystemExit(99)'])
            except FileExistsError:
                check(True)
            else:
                raise AssertionError('existing path accepted')
            check(p.read_bytes() == original and p.stat().st_ino == inode)
        for target, command in [(None, ['true']), (pathlib.Path('relative.private.log'), ['true']),
                                (root / 'wrong.log', ['true']), (root / 'empty.private.log', [])]:
            try: run(target, command)
            except ValueError: check(True)
            else: raise AssertionError('invalid boundary accepted')
        root.chmod(0o755)
        try: run(root / 'unsafe.private.log', ['true'])
        except ValueError: check(True)
        else: raise AssertionError('readable parent accepted')
        check(not (root / 'unsafe.private.log').exists())
        root.chmod(0o700)
    finally:
        os.umask(prior)
print(f'PG471_PRIVATE_COMMAND_TEST independentAssertions={checks} actualRootProbeReissued=false')
