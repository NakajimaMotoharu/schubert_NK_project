"""BUG1144: retain nested qualified class paths; old partial1642 untouched."""
import inspect
from pathlib import PurePosixPath
import pg1642_completed_candidate_compile as prior

TARGET = prior.W / 'pg1645-completed-unused-tools-v2'
ARCHIVE = prior.P / 'pg1646-release-v2.tar'


def canonical_relative(name):
    if type(name) is not str or not name or str(PurePosixPath(name)) != name or name.startswith('/') or any(p in ['', '.', '..'] for p in name.split('/')) or '\\' in name:
        raise ValueError('canonical nested inventory path required')
    return name


def inventory(root):
    return {canonical_relative(str(p.relative_to(root))): prior.sha(p) for p in root.rglob('*') if p.is_file()}


def write(path, raw):
    if path.is_relative_to(TARGET):
        canonical_relative(str(path.relative_to(TARGET)))
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    prior.write(path, raw)


def sources(bom):
    return {n: s.replace('pg1640-completed-unused-tools-v1', 'pg1645-completed-unused-tools-v2').replace('pg1643', 'pg1646').replace('pg1644-completed-unused-placement-v1', 'pg1647-completed-unused-placement-v2') for n, s in prior.sources(bom).items()}


def main():
    raw = inspect.getsource(prior.main).replace('pg1642-', 'pg1645-')
    raw = raw.replace("hashes = {p.name: sha(p) for p in TARGET.iterdir() if p.is_file()}", 'hashes = inventory(TARGET)')
    raw = raw.replace('for p in TARGET.iterdir():\n        p.chmod(0o400)', 'for p in TARGET.rglob("*"):\n        if p.is_file():\n            p.chmod(0o400)')
    raw = raw.replace("for name, digest in prior['fileHashes'].items():", "for name, digest in prior['fileHashes'].items():\n        canonical_relative(name)")
    ns = {**prior.__dict__, 'TARGET': TARGET, 'ARCHIVE': ARCHIVE, 'write': write, 'sources': sources, 'inventory': inventory, 'canonical_relative': canonical_relative}
    compile(raw, '<fixed nested shared class compiler>', 'exec')
    exec(raw, ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
