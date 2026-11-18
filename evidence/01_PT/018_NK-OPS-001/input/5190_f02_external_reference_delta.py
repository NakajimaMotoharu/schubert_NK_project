"""Resolve current external class name references against the already pinned public SDKs."""
from datetime import datetime, timezone
from pathlib import Path
import gzip
import runpy
from zipfile import ZipFile

ENTRY = Path(__file__).resolve()
h = runpy.run_path(str(ENTRY.with_name('5189_wbs66_four_module_delta_handoff.py')))
E = h['E']
D = h['D']
OUT = E / 'PG39622-f02-four-module-external-origins-delta-v1'


def external(rows):
    return {(origin, target) for origin, target, place in rows
            if place == 'not found' and not target.startswith(h['SOURCE_ROOT'])}


def graph_inputs(start):
    values = start['values']
    assert h['git']('rev-parse', 'HEAD').decode().strip() == values['source']
    assert h['git']('rev-parse', 'origin/dev-foundation').decode().strip() == values['source']
    assert all(h['ref'](Path(r['path'])) == r for r in values['oracleReferences'])
    path = h['matching_path']('PG39616*/manifest.json')
    evidence = h['load'](path)
    assert evidence['source'] == values['productionCoreMain'] and evidence['actualExit'] == 0
    assert evidence['f02PhysicalEdges']['current']['externalUnresolved'] == 385
    assert all(h['sha'](h['git']('show', f'{values["source"]}:{p}')) == key
               for p, key in evidence['sixPomDeclaration']['pomHashes'].items())
    return path, evidence['f02PhysicalEdges']


def origin_inputs():
    path = h['matching_path']('PG38330*/manifest.json')
    prior = h['load'](path)
    begin = h['revalidate_reference'](prior['commandRecord'])
    independent_file = path.with_name('independent-resolution.json')
    verified = h['load'](independent_file)
    assert verified['analysis'] == h['ref'](path)
    assert prior['actualToolExit'] == 0 and prior['stillNotFoundPairs'] == 0
    assert verified['actualExit'] == 0 and verified['priorMissingReferencesResolved'] == 379
    assert len(verified['typeOrigins']) == 52 and len(begin['externalJarPins']) == 47
    return path, independent_file, begin['externalJarPins'], verified['typeOrigins']


def build_member_index(pins, type_names):
    base = Path('../toolchain/m2/repository').resolve()
    paths = [Path(v['path']) for v in pins]
    assert len(set(paths)) == 47 and all(p.is_relative_to(base) and p.suffix == '.jar' and p.resolve() == p for p in paths)
    index = {n: [] for n in type_names}
    members = {n.replace('.', '/') + '.class': n for n in type_names}
    for pin, archive in zip(pins, paths, strict=True):
        assert h['ref'](archive) == pin
        with ZipFile(archive) as sdk:
            central_directory = sdk.namelist()
            for member, name in members.items():
                if member in central_directory:
                    assert central_directory.count(member) == 1
                    index[name].append(dict(archive=pin, member=member))
    return index


def main():
    start = h['load'](next(D.glob('470_*')))
    basefile, graph = graph_inputs(start)
    resolved_file, independent_path, pins, prior_origins = origin_inputs()
    previous_graph = h['revalidate_reference'](graph['historicalBaseline'])
    archived = Path(graph['historicalBaseline']['path']).with_name('jdeps.stdout.gz')
    assert h['ref'](archived)['sha256'] == previous_graph['evidence'][archived.name]
    delta = Path(graph['rawAnalysis']['path'])
    assert h['ref'](delta) == graph['rawAnalysis']
    previous_rows = h['edges'](gzip.decompress(archived.read_bytes()).decode())
    new_rows = h['edges'](gzip.decompress(delta.read_bytes()).decode())
    changed = set(graph['changedAndNewPhysical']) | set(graph['removed'])
    old = external(previous_rows)
    current = external([(a, b, c) for a, b, c in previous_rows if a not in changed] + new_rows)
    assert len(old) == 379 and len(current) == 385 and old <= current
    types = {to for _, to in current}
    assert set(prior_origins) < types and types - set(prior_origins) == {'javax.annotation.WillClose'}
    index = build_member_index(pins, types)
    out = {k: v[0] for k, v in sorted(index.items()) if len(v) == 1}
    assert out.keys() == types
    for name, value in prior_origins.items():
        assert Path(out[name]['archive']['path']).name == value['jar']
        assert out[name]['archive']['sha256'] == value['jarSha256']
        assert out[name]['member'] in value['matchingZipMembers']
    assert Path(out['javax.annotation.WillClose']['archive']['path']).name == 'jsr305-3.0.2.jar'
    details = OUT / 'external-origins.json'
    h['write'](details, dict(all385=sorted(current), addedSix=sorted(current - old), classOrigins=out))
    result = dict(actualExit=0, stage='F02-FOUR-MODULE-EXTERNAL-MEMBER-IDENTITY', startEvent=start['eventId'],
                  terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                  source=start['values']['productionCoreMain'], checkedHead=start['values']['source'],
                  currentFilesImmutable=True, oldReferencePairs=379, currentReferencePairs=385,
                  addedPairs=6, removedPairs=0, verifiedExternalTypes=53, newlyVerifiedTypes=1,
                  distinctProvidingJars=len({v['archive']['path'] for v in out.values()}),
                  checkedPublicArchives=47, unconfirmedNameReferences=0, ambiguousOrigins=0,
                  staticClasspathInspectionOnly=True, runtimeResolutionProved=False, wholeSixVerified=False,
                  freshBuilds=0, productTests=0, repeatedJdeps=0, externalBackendActions=0, newAcceptance=0,
                  evidence=[h['ref'](p) for p in (basefile, resolved_file, independent_path, details)],
                  verifier=h['ref'](ENTRY.relative_to(Path.cwd())))
    p = OUT / 'manifest.json'
    h['write'](p, result)
    print(h['ref'](p))


if __name__ == '__main__':
    main()
