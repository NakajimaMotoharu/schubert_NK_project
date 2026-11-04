"""Parse-only syntactic declaration/line reconciliation, never Product execution."""
import collections
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path.cwd()
DOCS = ROOT / 'documents/400_PGPT/470_PMO/500_SV計画整備_20261104'
SLOT = ROOT.parent / 'pgpt-runs/PG379/pg18542-sv80-method-line-parse-v1'
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18542-sv80-method-line-parse-v1'
JDK = ROOT.parent / 'toolchain/jdk-25.0.4/bin'
TOOL = ROOT / 'tools/quality/architecture/ExistingTestMethodJdkAudit.java'
HELD = {'SnapshotKeyCloseWitness.java', 'pg9892_snapshot_key_close_witness.py',
        'RootFailedStartRecoveryTest.java', 'RootFailedStartPairRecoveryTest.java'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def main():
    assert not SLOT.exists() and not OUT.exists()
    matrix = json.loads(next(DOCS.glob('503_*')).read_text())
    sources = {r['path']: r for r in matrix['rows'] if r['evidenceStatus'] == 'PARTIAL'}
    assert len(sources) == 80
    for name, row in sources.items():
        assert Path(name).name not in HELD and '/src/main/java/' in name
        assert sha(ROOT / name) == row['sha256']
    lines_path = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18532-sv80-line-static-resume-v1/manifest.json'
    assert sha(lines_path) == '6cbcf4309cfb2f7b91274fdb7875d7f8edea8e8a5466bc12c13e5da4c922c763'
    original = json.loads(lines_path.read_text())
    anchors = {s['path']: s['lineAnchors']
               for r in original['results'] + original['reusedStaticSuccess']
               for s in r['sourceRows']}
    assert set(anchors) == set(sources)
    tool_hash = sha(TOOL)
    SLOT.mkdir()
    OUT.mkdir()
    classes = SLOT / 'classes'
    classes.mkdir()
    catalog = SLOT / 'main-paths.txt'
    with catalog.open('x') as stream:
        stream.write('\n'.join(sorted(sources)) + '\n')
    empty = SLOT / 'empty.txt'
    with empty.open('x'):
        pass
    stages = []

    def run(label, command):
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=60, check=False)
        for kind, raw in [('stdout', result.stdout), ('stderr', result.stderr)]:
            with (SLOT / (label + '.' + kind)).open('xb') as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
        stage = dict(label=label, command=command, actualExit=result.returncode,
                     stdoutSha256=sha(SLOT / (label + '.stdout')),
                     stderrSha256=sha(SLOT / (label + '.stderr')),
                     stdoutBytes=len(result.stdout), stderrBytes=len(result.stderr))
        stages.append(stage)
        write(SLOT / (label + '.terminal.json'), stage)
        return result

    def checkpoint(status, **extra):
        write(OUT / 'manifest.json', dict(
            actualExit=status, source=matrix['source'], stages=stages,
            toolPath=str(TOOL.relative_to(ROOT)), toolSourceSha256=tool_hash,
            originalLineManifestSha256=sha(lines_path),
            compilerOperations=['JavacTask.parse'], analyzeInvoked=False,
            generateInvoked=False, productClassLoading=False, productExecution=False,
            newProductPT=0, coverageAdded=0, newAcceptance=0, formalUpdated=False, **extra))

    compiled = run('compile', [str(JDK / 'javac'), '--release', '25', '-proc:none',
                              '-Xlint:all', '-Werror', '-d', str(classes), str(TOOL)])
    if compiled.returncode:
        checkpoint(compiled.returncode, phase='TOOL_COMPILE_FAILED')
        raise SystemExit(compiled.returncode)
    command = [str(JDK / 'java'), '-cp', str(classes), TOOL.stem, str(ROOT)]
    legacy = run('legacy-default-vectors', command + [str(empty)])
    if legacy.returncode or legacy.stdout != b'SELFTEST\t7\n':
        checkpoint(1, phase='LEGACY_DEFAULT_CHECK_FAILED')
        raise SystemExit(1)
    parsed = run('parse-main80', command + [str(catalog), '--main-declarations'])
    if parsed.returncode:
        checkpoint(parsed.returncode, phase='PARSE_FAILED')
        raise SystemExit(parsed.returncode)
    observed = parsed.stdout.decode().splitlines()
    assert observed.pop(0) == 'SELFTEST\t15'
    declarations = collections.defaultdict(list)
    for line in observed:
        name, owner, method, parameters, start, end, first, last = line.split('\t')
        assert name in sources
        start, end, first, last = map(int, [start, end, first, last])
        assert 0 < start <= end and 0 <= first < last
        declarations[name].append(dict(
            id=f'{name}@{first}:{last}', syntacticOwner=owner, method=method,
            parameterCount=int(parameters), startLine=start, endLine=end,
            startOffset=first, endOffset=last))
    output_rows = []
    counts = collections.Counter()
    for name in sorted(sources):
        methods = declarations[name]
        assert len({m['id'] for m in methods}) == len(methods)
        line_rows = []
        for anchor in anchors[name]:
            candidates = [m for m in methods
                          if m['startLine'] <= anchor['sourceLine'] <= m['endLine']]
            if candidates:
                width = min(m['endOffset'] - m['startOffset'] for m in candidates)
                innermost = [m for m in candidates
                             if m['endOffset'] - m['startOffset'] == width]
                # Several declarations on one line cannot be disambiguated by JaCoCo's line alone.
                overlapping_siblings = any(
                    a['endOffset'] <= b['startOffset'] or b['endOffset'] <= a['startOffset']
                    for a in candidates for b in candidates if a is not b)
                disposition = ('AMBIGUOUS_SAME_LINE_DECLARATIONS'
                               if overlapping_siblings or len(innermost) != 1
                               else 'SYNTACTIC_ENCLOSING_DECLARATION_ONLY')
            else:
                innermost = []
                disposition = 'NO_EXPLICIT_METHOD_FIELD_OR_INITIALIZER_OR_GENERATED'
            counts[disposition] += 1
            line_rows.append(dict(**anchor, disposition=disposition,
                                  candidateDeclarationIds=[m['id'] for m in candidates],
                                  narrowestDeclarationIds=[m['id'] for m in innermost]))
        output_rows.append(dict(path=name, sourceSha256=sources[name]['sha256'],
                                declarations=methods, lineRows=line_rows))
    assert sum(len(r['lineRows']) for r in output_rows) == 7049
    assert sum(a['missedBranches'] for r in output_rows for a in r['lineRows']) == 3004
    for name, row in sources.items():
        assert sha(ROOT / name) == row['sha256']
    assert sha(TOOL) == tool_hash
    assert all(p.name.startswith(TOOL.stem) for p in classes.rglob('*.class'))
    # Negative inputs exercise this tool's own path/mode guard, never target source.
    negatives = []
    unknown = run('reject-unknown-mode', command + [str(empty), '--unknown-mode'])
    assert unknown.returncode != 0 and b'unknown declaration mode' in unknown.stderr
    negatives.append('UNKNOWN_MODE')
    for i, basename in enumerate(sorted(HELD)):
        rejected_catalog = SLOT / f'held-names-{i}.txt'
        with rejected_catalog.open('x') as stream:
            stream.write(basename + '\n')
        rejected = run(f'reject-held-name-{i}', command + [str(rejected_catalog), '--main-declarations'])
        assert rejected.returncode != 0 and b'held source excluded by name' in rejected.stderr
        negatives.append(basename)
    write(OUT / 'method-line-map.json', output_rows)
    checkpoint(0, phase='COMPLETE_STATIC_SYNTAX_ONLY', sourceFiles=80,
               declarations=sum(len(r['declarations']) for r in output_rows),
               lineAnchors=7049, missedBranches=3004, dispositions=dict(counts),
               methodLineMapSha256=sha(OUT / 'method-line-map.json'),
               legacyVectors=7, mainVectors=8, commandRejectionVectors=negatives,
               notJvmMethodIdentity=True, noSyntheticClassOrInitializerExclusion=True,
               noIndependentBusinessOracleQualification=True)
    print(json.dumps(dict(actualExit=0, sourceFiles=80, lineAnchors=7049,
                          missedBranches=3004, dispositions=dict(counts),
                          manifestSha256=sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    try:
        main()
    except Exception as failure:
        if OUT.is_dir() and not (OUT / 'manifest.json').exists():
            write(OUT / 'manifest.json', dict(
                actualExit=1, phase='TOOL_OR_POSTCONDITION_FAILURE',
                errorType=type(failure).__name__, newProductPT=0,
                coverageAdded=0, newAcceptance=0))
        raise
