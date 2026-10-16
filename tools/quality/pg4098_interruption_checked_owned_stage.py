"""New-only frozen stage after BUG1337; preserves all earlier operational artifacts."""
import inspect
import sys
import types
import pg4088_failed_done_owned_compile as compiler
import pg4088_failed_done_owned_sources as source
import pg4090_failed_done_owned_inspection as inspector
import pg4058_original_read_profile as transport
from pg4060_original_profile_dual_stack import once

TOOLS = 'pg4098-interruption-checked-owned-tools-v1'
INSPECT = 'pg4100-interruption-checked-owned-inspect-v1'


def role():
    return types.SimpleNamespace(**{**vars(source), 'TOOLS': TOOLS, 'INSPECT': INSPECT})


def payload(action):
    if action not in {'compile', 'inspect'}:
        raise ValueError('compile or inspect only; no recovery dispatcher')
    module = compiler if action == 'compile' else inspector
    namespace = {**vars(module), 'role': role()}
    exec(compile(inspect.getsource(module.payload), '<new frozen operational stage>', 'exec'), namespace)
    raw = namespace['payload']()
    if action == 'inspect':
        old = " p=frozen/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p));require(hashlib.sha256(p.read_bytes()).hexdigest()==digest and p.lstat()==s)"
        new = " p=frozen/name;m=metadata(p);s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p));require(hashlib.sha256(p.read_bytes()).hexdigest()==digest and metadata(p)==m)"
        raw = once(raw, old, new)
    compile(raw, '<new interruption-checked operational stage>', 'exec')
    return raw


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {'compile', 'inspect'}:
        raise SystemExit('compile or inspect')
    action = sys.argv[1]
    namespace = {**vars(transport), 'payload': lambda unused: payload(action),
                 'SLOT': TOOLS if action == 'compile' else INSPECT,
                 'sys': types.SimpleNamespace(argv=['new_stage', 'compile' if action == 'compile' else 'run'])}
    exec(compile(inspect.getsource(transport.main), '<new stage transport>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
