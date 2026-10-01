"""COLLECTATIME001: real independent-reader IO; public temporary fixture only."""
import ast
import os
import pathlib
import stat
import subprocess
import tempfile

source = pathlib.Path('/home/ubuntu/pg405-stage/pg404_read_permit_fixed.py')
tree = ast.parse(source.read_text())
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in ['stable', 'read']]
assert len(functions) == 2 and os.geteuid() == 0
with tempfile.TemporaryDirectory(prefix='pg405-atime-', dir='/var/lib/pgpt-s1-preservation') as temporary:
    root = pathlib.Path(temporary)
    fixture = root / 'epoch.current'
    fixture.write_bytes(b'NKCOLLECTOR-PUBLIC-ATIME\n')
    fixture.chmod(0o600)
    os.utime(fixture, ns=(1, fixture.stat().st_mtime_ns))
    before = fixture.stat()
    namespace = {'root': root, 'os': os, 'stat': stat, 'subprocess': subprocess}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), 'exec'), namespace)
    assert namespace['read']('epoch.current') == b'NKCOLLECTOR-PUBLIC-ATIME\n'
    after = fixture.stat()
    assert after.st_atime_ns != before.st_atime_ns
    assert namespace['stable'](before) == namespace['stable'](after)
    fixture.chmod(0o640)
    try:
        namespace['read']('epoch.current')
        raise RuntimeError('mode mutation falsely accepted')
    except AssertionError:
        pass
    fixture.chmod(0o600)
    class MutatingRead:
        def __getattr__(self, name):
            return getattr(os, name)
        def read(self, descriptor, length):
            result = os.read(descriptor, length)
            if result:
                fixture.write_bytes(b'NKCOLLECTOR-PUBLIC-CHANGED\n')
            return result
    namespace['os'] = MutatingRead()
    try:
        namespace['read']('epoch.current')
        raise RuntimeError('content mutation falsely accepted')
    except AssertionError:
        pass
print('COLLECTATIME001 PASS actualAtimeChange=true stableNineFields=true modeMutationRejected=true contentMutationRejected=true publicFixtureRemoved=true')
