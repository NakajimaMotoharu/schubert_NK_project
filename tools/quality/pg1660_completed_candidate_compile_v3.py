"""New frozen compiler after normal noDB recovery; prior slots remain unchanged."""
import inspect
import pg1642_completed_candidate_compile as engine
import pg1645_completed_candidate_compile_v2 as nested
from pg1659_completed_candidate_identity_sources import sources, TOOLS

TARGET = engine.W / TOOLS
ARCHIVE = engine.P / 'pg1661-release-v3.tar'


def write(path, raw):
    if path.is_relative_to(TARGET):
        nested.canonical_relative(str(path.relative_to(TARGET)))
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    engine.write(path, raw)


def compiler():
    raw = inspect.getsource(engine.main).replace('pg1642-', 'pg1660-').replace('pg1641-completed-current-before-v2/manifest.safe.json', 'pg1658-owned-recovery-independent-post-v1/manifest.safe.json')
    raw = raw.replace("hashes = {p.name: sha(p) for p in TARGET.iterdir() if p.is_file()}", 'hashes = inventory(TARGET)')
    raw = raw.replace('for p in TARGET.iterdir():\n        p.chmod(0o400)', 'for p in TARGET.rglob("*"):\n        if p.is_file():\n            p.chmod(0o400)')
    raw = raw.replace("for name, digest in prior['fileHashes'].items():", "for name, digest in prior['fileHashes'].items():\n        canonical_relative(name)")
    raw = raw.replace("'Pg1640OriginalTupleTest.java']", "'Pg1640OriginalTupleTest.java','Pg1660CurrentIdentityTest.java']")
    raw = raw.replace("('original', 'Pg1640OriginalTupleTest')", "('original', 'Pg1640OriginalTupleTest'),('identity','Pg1660CurrentIdentityTest')")
    compile(raw, '<new recovered current candidate four-identity compiler>', 'exec')
    return raw


def main():
    ns = {**engine.__dict__, 'TARGET': TARGET, 'ARCHIVE': ARCHIVE, 'write': write, 'sources': sources, 'inventory': nested.inventory, 'canonical_relative': nested.canonical_relative}
    exec(compiler(), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
