"""Refresh F02 static edges only for the one changed class, preserving the archive pair."""
from datetime import datetime, timezone
from pathlib import Path
import gzip
import hashlib
import json
import re
import subprocess

OPS = Path('evidence/01_PT/018_NK-OPS-001')
E = OPS / 'evidence'
OLD = E / 'PG39462-admission-single-cleanup-four-build-v2/compile/manifest.json'
NEW = E / 'PG39764-process-resource-scope-four-main-v1/compile/manifest.json'
PREVIOUS = E / 'PG39616-wbs66-four-module-edge-and-handoff-v1/manifest.json'
EXTERNAL = E / 'PG39622-f02-four-module-external-origins-delta-v1/manifest.json'
START = Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/493_F02単一物理の境界確認開始.json')
CLASS = 'dev.codex.schubert.nk.batch.platform.ProcessResourceScope'
ENTRY = CLASS.replace('.', '/') + '.class'


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def write(path, data):
    with path.open('x') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def observe(manifest, output, phase, jdeps):
    work = Path(manifest['cwd'])
    assert work.is_relative_to(Path.cwd().parent / 'pgpt-runs/PG379')
    p = work / 'src/schubert-nk-batch/target/classes' / ENTRY
    assert p.resolve()==p and ref(p)['sha256']==manifest['physicalClassHashes']['batch'][ENTRY]
    command = [str(jdeps), '-verbose:class', '-filter:none', '--ignore-missing-deps', str(p)]
    r = subprocess.run(command, capture_output=True, timeout=20)
    assert r.returncode == 0 and not r.stderr
    rows = {}
    for line in r.stdout.decode().splitlines():
        if not line.startswith(' '):
            continue
        parsed = re.fullmatch(r'\s+(\S+)\s+->\s+(\S+)\s+(\S.*)', line)
        assert parsed and parsed[1] == CLASS and parsed[2] not in rows
        rows[parsed[2]] = parsed[3]
    data = output / (phase + '-jdeps.stdout')
    with data.open('xb') as out:
        out.write(r.stdout)
    return dict(command=command, actualExit=r.returncode, stdout=ref(data), changedClass=ref(p), edges=rows)


def archive_compile(output, manifest):
    result = []
    for name, h in manifest['logs'].items():
        source = NEW.with_name(name)
        data = source.read_bytes()
        assert sha(data) == h
        target = output / (name + '.gz')
        with target.open('xb') as f:
            f.write(gzip.compress(data, mtime=0))
        assert gzip.decompress(target.read_bytes()) == data
        result.append(dict(originalPath=str(source), originalSha256=h, archive=ref(target)))
    return result


def main():
    start = read(START)
    root = E / start['values']['run']
    baseline, build, prev, ext = map(read, (OLD, NEW, PREVIOUS, EXTERNAL))
    assert build['sourceCore'] == start['values']['productionCoreMain']
    assert baseline['sourceCore'] == build['baselineSource'] == prev['originalBuildSource']
    assert all(x['actualExit']==0 for x in (baseline,build,prev,ext))
    assert not any(x['productTestsExecuted'] for x in (baseline,build))
    old, new = [{(m,n):h for m, types in s['physicalClassHashes'].items() for n,h in types.items()}
                for s in (baseline,build)]
    assert old.keys()==new.keys() and len(old)==1101
    assert [key for key in sorted(old) if old[key]!=new[key]] == [('batch', ENTRY)]
    assert prev['currentFourEligibleSourceEquality']['all490']
    assert prev['buildReceipt']==ref(OLD)
    assert ext['currentReferencePairs']==385 and ext['unconfirmedNameReferences']==ext['ambiguousOrigins']==0
    jdeps=Path.cwd().parent / 'toolchain/jdk-25.0.4/bin/jdeps'
    before = observe(baseline, root, 'before', jdeps)
    after = observe(build, root, 'after', jdeps)
    removed = sorted(set(before['edges']).difference(after['edges']))
    added = sorted(set(after['edges']).difference(before['edges']))
    assert not removed and added==['java.lang.AssertionError']
    assert after['edges'][added[0]]=='java.base'
    assert all(after['edges'][typ]==kind for typ,kind in before['edges'].items())
    count = prev['f02PhysicalEdges']['current']
    current = dict(count, total=count['total']+len(added), externalUnresolved=0)
    assert prev['f02PhysicalEdges']['storageSqlEdgeStillOpen']
    manifest=dict(actualExit=0,groupStart=start['eventId'],source=build['sourceCore'],
                  unchangedPhysical=1100,checkedPhysicalDelta=1,baseline=ref(PREVIOUS),
                  thirdPartyProof=ref(EXTERNAL),normalCurrentFourModuleCompile=ref(NEW),
                  tool=ref(jdeps),deltaBefore=before,deltaAfter=after,
                  removed=removed,addedJdkTypes=added,newInternalEdges=0,newThirdPartyEdges=0,
                  priorExternalStaticExactPairs=385,currentTypedEdgeSummary=current,
                  buildStdoutStderrArchives=archive_compile(root,build),productTests=0,
                  newBuilds=0,actualServiceOrHostVerification=False,apiAndWebTyped=False,
                  wholeF02Accepted=False,whole451Accepted=False,newAcceptance=0,
                  verifier=ref(Path(__file__)),terminalAtUTC=datetime.now(timezone.utc).isoformat())
    write(root/'manifest.json',manifest)
    print(ref(root/'manifest.json'))


if __name__=='__main__':
    main()
