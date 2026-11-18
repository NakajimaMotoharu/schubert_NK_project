"""Bind each scanner coordinate to the current allowed artifact provenance or report it open."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import gzip

ENTRY = Path(__file__).resolve()
spec = spec_from_file_location('g07_business_range', ENTRY.with_name('5196_g07_business_outbox_delta.py'))
r = module_from_spec(spec)
spec.loader.exec_module(r)

p = r.load('g07_business_base_proof', '5182_g07_jdbc_metrics_cached_classification.py')
r.configure(p.t.WRAPPER)
p.OUT = p.t.OUT = p.B.OUT = r.OUT
p.WORK = p.t.WORK = p.B.WORK = r.TEMP
p.t.PREPARE_RUNS = ('PG39588', 'PG39638', 'PG39642', 'PG39647')
p.t.ORDINARY_BUILD_RUNS = ()
B = p.B
E = r.E
TC = Path.cwd().parent / 'toolchain'
PREVIOUS = E / 'PG39580-g07-published-jdbc-web-monitoring-delta-v1/manifest.json'
CRC_RUNS = ('PG39600', 'PG39654')


def known_coordinate_lines():
    original, ref = p_previous()
    m = B.load(PREVIOUS)
    assert m['qualifiedRangeOnly'] and m['confirmedSecrets'] == m['unresolvedCandidates'] == 0
    from_file = m['exactPrivateProofFiles']
    for key in ('classified-findings.json', 'additional-build-origins.json'):
        path = Path(from_file[key]['path'])
        assert path.is_relative_to(r.RETAIN.parent) and B.ref(path) == from_file[key]
        for row in B.load(path):
            if row['ground'] is not None:
                original.add((row['rule'], row['lineSha256'], row['startColumn'], row['endColumn']))
    return original, B.ref(PREVIOUS)


def current_crc(location, key, value):
    if len(value) != 16:
        return None
    if any(location.parent.name.startswith(prefix + '-') for prefix in CRC_RUNS):
        if location.name != 'manifest.json':
            return None
        m = B.load(location)
        if m['classIds'].get(key) != value:
            return None
        file = location.with_name('unit-execinfo.stdout')
        data = file.read_bytes() if file.is_file() else gzip.decompress(file.with_suffix('.stdout.gz').read_bytes())
        assert B.sha(data) == m['files'][file.name]
        exact = [line for line in data.decode().splitlines() if line.split() and line.split()[-1] == key]
        if len(exact) == 1 and exact[0].split()[0] == value:
            return dict(kind='Observed class identity on same fixed local JaCoCo execution',
                        qualifier=B.ref(location), classReference=key)
    return None


def resolved_type_origins():
    qualified = next(E.glob('PG39622*/manifest.json'))
    m = B.load(qualified)
    assert m['actualExit'] == m['ambiguousOrigins'] == m['unconfirmedNameReferences'] == 0
    detail = qualified.with_name('external-origins.json')
    assert B.ref(detail) in m['evidence']
    entries = B.load(detail)['classOrigins']
    result = {}
    for value in entries.values():
        file = Path(value['archive']['path'])
        assert file.is_relative_to(TC/'m2/repository') and file.suffix == '.jar'
        digest = value['archive']['sha256']
        if digest not in result:
            assert B.ref(file) == value['archive']
            result[digest] = dict(kind='Current fixed public SDK archive bytes', archive=B.ref(file),
                                  qualifier=B.ref(qualified))
    assert len(result) == m['distinctProvidingJars']
    return result


def current_class_digests():
    qualified = next(E.glob('PG39616*/manifest.json'))
    m = B.load(qualified)
    assert m['actualExit'] == 0 and m['f02PhysicalEdges']['protectedClassesRead'] == 0
    ref = m['buildReceipt']
    assert B.ref(Path(ref['path'])) == ref
    build = B.load(Path(ref['path']))
    result = {}
    for key, sha in m['f02PhysicalEdges']['changedAndNewPhysical'].items():
        rel = key.replace('.', '/') + '.class'
        assert Path(rel).stem.split('$')[0] not in B.HELD
        [module] = [module for module, classes in build['physicalClassHashes'].items()
                    if classes.get(rel) == sha]
        target = Path(build['cwd']) / f'src/schubert-nk-{module}/target/classes' / rel
        assert target.is_relative_to(r.RETAIN.parent) and B.ref(target)['sha256'] == sha
        result[sha] = dict(kind='Typed bytecode-delta source class content digest',
                           classReference=key, qualifier=B.ref(qualified))
    return result


def proven_content(line, first, last, digests, reachable):
    return p_content(line, first, last, digests | explicit_origins, reachable)


p_previous = p.exact_previous
p_content = p.proven_content
p.exact_previous = known_coordinate_lines
p.t.checked_run_id = current_crc
explicit_origins = {}
if __name__ == '__main__':
    explicit_origins.update({k.encode(): v for k, v in (resolved_type_origins() | current_class_digests()).items()})
    p.proven_content = proven_content
    p.main()
