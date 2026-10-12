"""New current-normal stage/place after independently closed owned recovery."""
import inspect
import sys
import pg1648_completed_unused_dispatch_v2 as previous
import pg1660_completed_candidate_compile_v3 as compiler
from pg1659_completed_candidate_identity_sources import sources

GUEST = '/var/lib/pgpt-s1-preservation/pg1659-completed-unused-tools-v3'
REMOTE = '/home/ubuntu/pg1661-candidate-input-v1'
STAGE = previous.prior.STAGE.replace('pg1646', 'pg1661').replace('PG1646', 'PG1661').replace('pg1645-completed-unused-tools-v2', 'pg1659-completed-unused-tools-v3')


def namespace(candidate):
    ns = previous.namespace(candidate)
    ns.update(TARGET=compiler.TARGET, GUEST=GUEST, REMOTE=REMOTE, STAGE=STAGE, sources=sources)
    return ns


def source():
    raw = previous.source()
    for a, b in [('pg1648-', 'pg1661-'), ('pg1645-frozen-v1.safe.json', 'pg1660-frozen-v1.safe.json'), ('pg1641-completed-current-before-v2/manifest.safe.json', 'pg1658-owned-recovery-independent-post-v1/manifest.safe.json'), ('pg1645-completed-unused-tools-v2', 'pg1659-completed-unused-tools-v3'), ('pg1646', 'pg1661'), ('pg1661-release-v2.tar', 'pg1661-release-v3.tar')]:
        raw = raw.replace(a, b)
    raw = raw.replace("'Pg1640NativeArgumentTest','Pg1640UnusedStage place'", "'Pg1640NativeArgumentTest','Pg1660CurrentIdentityTest','Pg1640UnusedStage place'")
    compile(raw, '<new complete current normal candidate dispatcher>', 'exec')
    return raw


def main():
    if sys.argv[1:] not in (['stage'], ['place']):
        raise ValueError('closed new stage/place required')
    code = inspect.getsource(previous.main)
    ns = {**previous.__dict__, 'namespace': namespace, 'source': source}
    exec(compile(code, '<new recovered current dispatcher main>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
