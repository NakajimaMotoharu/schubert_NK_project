"""BUG1336: exact existing nine-attribute helper; reuse frozen operational classes unchanged."""
import inspect
import pg4090_failed_done_owned_inspection as previous
import pg4058_original_read_profile as transport
from pg4060_original_profile_dual_stack import once

SLOT = 'pg4094-failed-done-owned-inspect-v1'


def payload():
    raw = previous.payload().replace(previous.role.INSPECT, SLOT)
    old = " p=frozen/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p));require(hashlib.sha256(p.read_bytes()).hexdigest()==digest and p.lstat()==s)"
    new = " p=frozen/name;m=metadata(p);s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p));require(hashlib.sha256(p.read_bytes()).hexdigest()==digest and metadata(p)==m)"
    return once(raw, old, new)


def main():
    namespace = {**transport.__dict__, 'payload': lambda action: payload(), 'SLOT': SLOT}
    namespace['sys'] = type('InspectOnlyArguments', (), {'argv': ['inspect_stage', 'run']})
    exec(compile(inspect.getsource(transport.main), '<nine-attribute inspect only>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
