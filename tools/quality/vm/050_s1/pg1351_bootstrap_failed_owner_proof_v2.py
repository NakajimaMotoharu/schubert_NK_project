"""New-only exact Java exe/argv discovery; wrapper is never an owned actor."""
import pg1350_bootstrap_failed_owner_proof as prior
from pg1334_published_owned_stop_sources_v2 import SOURCE

def candidate(argv, exe):
    return type(argv) is bytes and type(exe) is str and exe == '/opt/jdk-25.0.4/bin/java' and b'Pg1348BootstrapExisting\x00verify\x00' in argv

def payload(seals):
    raw = prior.payload(seals)
    old = "try:a=(p/'cmdline').read_bytes()"
    if raw.count(old) != 1:
        raise ValueError('one actual discovery required')
    raw = raw.replace(old, "try:a=(p/'cmdline').read_bytes();exe=str((p/'exe').readlink())")
    old = "if b'Pg1348BootstrapExisting\\x00verify\\x00' in a:candidates.append((p,a))"
    if raw.count(old) != 1:
        raise ValueError('one actual argv candidate boundary required')
    import inspect
    marker = 'def fixed_owner():'
    raw = raw.replace(marker, inspect.getsource(candidate) + '\n' + marker)
    raw = raw.replace(old, 'if candidate(a,exe):candidates.append((p,a))')
    raw = raw.replace('pg1350-bootstrap-failed-owner-v1', 'pg1351-bootstrap-failed-owner-v2').replace('PG1350-bootstrap-failed-owner-v1', 'PG1351-bootstrap-failed-owner-v2')
    compile(raw, '<actual Java-only current owner>', 'exec')
    return raw

def source():
    return prior.source().replace('pg1350-bootstrap-failed-owner-v1', 'pg1351-bootstrap-failed-owner-v2')

def main():
    env = dict(prior.prior.previous.transport.__dict__, SOURCE=SOURCE, payload=payload)
    exec(compile(source(), '<current Java-only proof transport>', 'exec'), env)
    return env['main']()

if __name__ == '__main__':
    raise SystemExit(main())
