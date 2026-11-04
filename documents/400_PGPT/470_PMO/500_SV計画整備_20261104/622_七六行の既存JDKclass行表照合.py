"""Read existing class line tables with javap; never load or execute Product classes."""
import collections
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path.cwd()
DOCS = ROOT / 'documents/400_PGPT/470_PMO/500_SV計画整備_20261104'
SLOT = ROOT.parent / 'pgpt-runs/PG379/pg18548-sv76-javap-line-resume-v1'
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18548-sv76-javap-line-resume-v1'
ORIGINAL_SLOT = ROOT.parent / 'pgpt-runs/PG379/pg18546-sv76-javap-line-v1'
JAVAP = ROOT.parent / 'toolchain/jdk-25.0.4/bin/javap'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def attach_code_lines(text, prior_methods):
    """Use independently retained descriptors; instruction text is never a declaration."""
    methods = [{**method, 'lines': []} for method in prior_methods]
    by_header = {method['declaration']: method for method in methods}
    assert len(by_header) == len(methods)
    seen, current = set(), None
    for raw_line in text.splitlines():
        value = raw_line.strip()
        if raw_line.startswith('  ') and not raw_line.startswith('   ') and value.endswith(';'):
            if value in by_header:
                assert value not in seen
                seen.add(value)
                current = by_header[value]
            else:
                assert '(' not in value and value != 'static {};'
                current = None
        elif current is not None:
            line = re.fullmatch(r'line (\d+): (\d+)', value)
            if line:
                current['lines'].append(dict(sourceLine=int(line.group(1)), pc=int(line.group(2))))
    assert seen == set(by_header)
    return methods


def code_line_vectors():
    prior = [dict(name='m', declaration='public java.lang.String m();', descriptor='()Ljava/lang/String;'),
             dict(name='<init>', declaration='public T();', descriptor='()V'),
             dict(name='<clinit>', declaration='static {};', descriptor='()V')]
    sample = ('  public java.lang.String m();\n    Code:\n'
              '       0: ldc #1 // String fake();\n    LineNumberTable:\n      line 7: 0\n'
              '  public T();\n    Code:\n    LineNumberTable:\n      line 8: 0\n'
              '  static {};\n    Code:\n    LineNumberTable:\n      line 9: 0\n')
    observed = attach_code_lines(sample, prior)
    assert [x['lines'] for x in observed] == [
        [dict(sourceLine=7, pc=0)], [dict(sourceLine=8, pc=0)], [dict(sourceLine=9, pc=0)]]
    assert observed[0]['descriptor'] == '()Ljava/lang/String;'
    for bad in [sample + '  public T();\n', sample.replace('  public T();\n', ''),
                sample + '  public void invented();\n']:
        try:
            attach_code_lines(bad, prior)
        except AssertionError:
            continue
        raise AssertionError('code-line parser must reject missing/duplicate/unknown header')


def missing_line_tables():
    """Supplement the missing attribute; do not reacquire successful declaration facts."""
    global SLOT, OUT
    SLOT = ROOT.parent / 'pgpt-runs/PG379/pg18550-sv76-code-line-only-v1'
    OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18550-sv76-code-line-only-v1'
    assert not SLOT.exists() and not OUT.exists()
    code_line_vectors()
    original = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18548-sv76-javap-line-resume-v1'
    manifest_path = original / 'manifest.json'
    assert sha(manifest_path) == '3696a96a38fe1d7cfe15e953d19c75c3f9c571834035ed126425b65715449397'
    manifest = json.loads(manifest_path.read_text())
    assert manifest['actualExit'] == 0 and manifest['exactMatchAnchors'] == 0
    assert sha(original / 'class-line-map.json') == manifest['classLineMapSha256']
    old = json.loads((original / 'class-line-map.json').read_text())
    assert len(old['classes']) == len(manifest['stages']) == 37 and len(old['rows']) == 76
    for row in old['rows']:
        assert sha(ROOT / row['path']) == row['sourceSha256']
    os.umask(0o077)
    SLOT.mkdir()
    OUT.mkdir()
    child_env = dict(os.environ)
    for key in ['CLASSPATH', 'JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS']:
        child_env.pop(key, None)
    stages, classes, rows = [], [], []
    for index, (previous, prior_stage) in enumerate(zip(old['classes'], manifest['stages'], strict=True), 1):
        class_path = Path(prior_stage['command'][-1])
        assert sha(class_path) == previous['classSha256']
        command = [str(JAVAP), '-p', '-c', '-l', str(class_path)]
        result = subprocess.run(command, cwd=ROOT, env=child_env, capture_output=True, timeout=60, check=False)
        for kind, content in [('stdout', result.stdout), ('stderr', result.stderr)]:
            with (SLOT / f'{index:03}.{kind}').open('xb') as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        stage = dict(command=command, actualExit=result.returncode,
                     stdoutSha256=sha(SLOT / f'{index:03}.stdout'),
                     stderrSha256=sha(SLOT / f'{index:03}.stderr'),
                     stdoutBytes=len(result.stdout), stderrBytes=len(result.stderr))
        stages.append(stage)
        write(SLOT / f'{index:03}.terminal.json', stage)
        assert result.returncode == 0
        methods = attach_code_lines(result.stdout.decode(), previous['methods'])
        classes.append({**previous, 'methods': methods})
        for anchor in [x for x in old['rows'] if x['physical'] == previous['physical']]:
            candidates = []
            for method in methods:
                pcs = [line['pc'] for line in method['lines'] if line['sourceLine'] == anchor['sourceLine']]
                if pcs:
                    candidates.append(dict(name=method['name'], descriptor=method['descriptor'], pcs=pcs))
            rows.append({**anchor, 'jvmMethodCandidates': candidates,
                         'jvmDisposition': 'EXACT_CLASS_LINE_TABLE_CANDIDATES' if candidates
                         else 'NO_EXACT_LINE_TABLE_MATCH_REQUIRES_FURTHER_RECONCILIATION'})
        assert sha(class_path) == previous['classSha256']
    assert len(rows) == 76
    for row in rows:
        assert sha(ROOT / row['path']) == row['sourceSha256']
    write(OUT / 'class-line-map.json', dict(classes=classes, rows=rows))
    matched = sum(bool(x['jvmMethodCandidates']) for x in rows)
    value = dict(actualExit=0 if matched == 76 else 2, source=manifest['source'],
                 sourceFiles=21, physicalClasses=37, lineAnchors=76, exactMatchAnchors=matched,
                 ambiguousCandidateAnchors=sum(len(x['jvmMethodCandidates']) > 1 for x in rows),
                 reusedDeclarationClasses=37, newDeclarationQualification=0,
                 newCodeLineTableInvocations=37, stages=stages,
                 parserPositiveCases=['REFERENCE_DESCRIPTOR', 'CONSTRUCTOR', 'CLINIT', 'INSTRUCTION_NOT_HEADER'],
                 parserNegativeCases=['DUPLICATE_HEADER', 'MISSING_HEADER', 'UNKNOWN_HEADER'],
                 classLineMapSha256=sha(OUT / 'class-line-map.json'),
                 priorManifestSha256=sha(manifest_path), scriptSha256=sha(Path(__file__)),
                 productClassesLoaded=False, productExecution=False, oldExecRead=False,
                 newProductPT=0, coverageAdded=0, newAcceptance=0, formalUpdated=False,
                 rawInstructionsPublished=False)
    write(OUT / 'manifest.json', value)
    print(json.dumps({k: value[k] for k in ['actualExit', 'lineAnchors', 'exactMatchAnchors',
                                            'ambiguousCandidateAnchors', 'reusedDeclarationClasses']}))
    raise SystemExit(value['actualExit'])


def main():
    assert not SLOT.exists() and not OUT.exists()
    preflight = json.loads(next(DOCS.glob('621_*')).read_text())
    normal_path = Path(preflight['originalNormalManifest'])
    assert sha(normal_path) == preflight['normalManifestSha256']
    normal = json.loads(normal_path.read_text())
    assert normal['actualExit'] == 0 and normal['source'] == preflight['source']
    facts = json.loads(next(DOCS.glob('613_*')).read_text())
    anchors = facts['unmappedAnchors']
    assert len(anchors) == 76
    by_class = collections.defaultdict(list)
    for anchor in anchors:
        assert not set(anchor) & {
            'sourceSha256', 'classSha256', 'jarModule', 'jvmMethodCandidates', 'jvmDisposition'}
        path = anchor['path']
        assert '/src/main/java/' in path
        assert Path(path).name not in {
            'SnapshotKeyCloseWitness.java', 'RootFailedStartRecoveryTest.java',
            'RootFailedStartPairRecoveryTest.java', 'pg9892_snapshot_key_close_witness.py'}
        assert sha(ROOT / path) == normal['begin']['inputHashes'][path]
        assert re.fullmatch(r'[A-Za-z0-9_$/]+', anchor['physical'])
        by_class[anchor['physical']].append(anchor)
    assert sorted(by_class) == preflight['targetPhysicalClasses'] and len(by_class) == 37
    jars = normal['jars']
    entries = {}
    for module, jar in jars.items():
        path = Path(jar['path'])
        assert sha(path) == jar['sha256']
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            for physical in by_class:
                entry = physical + '.class'
                assert names.count(entry) <= 1
                if entry in names:
                    assert physical not in entries
                    entries[physical] = (module, archive.read(entry))
    assert set(entries) == set(by_class)
    preserved = json.loads(next(DOCS.glob('624_*')).read_text())
    original_stage = json.loads((ORIGINAL_SLOT / '001.terminal.json').read_text())
    assert original_stage == preserved['firstStaticJavapTerminal']
    assert original_stage['actualExit'] == 0
    assert sha(ORIGINAL_SLOT / '001.stdout') == original_stage['stdoutSha256']
    assert sha(ORIGINAL_SLOT / '001.stderr') == original_stage['stderrSha256']
    SLOT.mkdir()
    OUT.mkdir()
    extracted = SLOT / 'class-bytes'
    extracted.mkdir()
    child_env = dict(os.environ)
    for key in ['CLASSPATH', 'JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS']:
        child_env.pop(key, None)
    stages, classes, rows = [], [], []
    for index, physical in enumerate(sorted(by_class), 1):
        module, raw = entries[physical]
        class_path = extracted / (physical + '.class')
        class_path.parent.mkdir(parents=True, exist_ok=True)
        with class_path.open('xb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        command = [str(JAVAP), '-p', '-s', '-l', '-sysinfo', str(class_path)]
        if index == 1:
            # Original javap completed before the row merger failed; do not replay it.
            assert sha(Path(original_stage['command'][-1])) == hashlib.sha256(raw).hexdigest()
            command = original_stage['command']
            result = subprocess.CompletedProcess(
                command, original_stage['actualExit'],
                (ORIGINAL_SLOT / '001.stdout').read_bytes(),
                (ORIGINAL_SLOT / '001.stderr').read_bytes())
        else:
            result = subprocess.run(command, cwd=ROOT, env=child_env,
                                    capture_output=True, timeout=60, check=False)
        for kind, content in [('stdout', result.stdout), ('stderr', result.stderr)]:
            with (SLOT / f'{index:03}.{kind}').open('xb') as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        stage = dict(command=command, actualExit=result.returncode,
                     stdoutSha256=sha(SLOT / f'{index:03}.stdout'),
                     stderrSha256=sha(SLOT / f'{index:03}.stderr'),
                     stdoutBytes=len(result.stdout), stderrBytes=len(result.stderr),
                     executedThisInvocation=index != 1,
                     reusedOriginalTerminal='PG18546/001' if index == 1 else None)
        stages.append(stage)
        write(SLOT / f'{index:03}.terminal.json', stage)
        if result.returncode:
            write(OUT / 'manifest.json', dict(actualExit=result.returncode,
                  source=normal['source'], phase='JAVAP_FAILED', stages=stages,
                  newProductPT=0, coverageAdded=0, newAcceptance=0))
            raise SystemExit(result.returncode)
        text = result.stdout.decode()
        expected_hash = hashlib.sha256(raw).hexdigest()
        assert re.search(r'SHA-256 checksum\s+' + expected_hash, text)
        declared_source = re.search(r'Compiled from "([^"\n]+)"', text)
        source_paths = {a['path'] for a in by_class[physical]}
        assert len(source_paths) == 1
        source_path = next(iter(source_paths))
        assert declared_source and declared_source.group(1) == Path(source_path).name
        methods, current = [], None
        for line in text.splitlines():
            value = line.strip()
            if value.startswith('descriptor:'):
                if current is not None:
                    current['descriptor'] = value.removeprefix('descriptor:').strip()
                continue
            if value == 'static {};':
                current = dict(name='<clinit>', declaration=value, lines=[])
                methods.append(current)
            elif value.endswith(';') and '(' in value:
                token = value.split('(', 1)[0].split()[-1]
                name = '<init>' if token == physical.replace('/', '.') else token
                current = dict(name=name, declaration=value, lines=[])
                methods.append(current)
            elif value.endswith(';') and not value.startswith('descriptor:'):
                current = None
            elif current is not None:
                match = re.fullmatch(r'line (\d+): (\d+)', value)
                if match:
                    current['lines'].append(dict(sourceLine=int(match.group(1)), pc=int(match.group(2))))
        assert methods and all(m.get('descriptor', '').startswith('(') for m in methods)
        assert len({(m['name'], m['descriptor']) for m in methods}) == len(methods)
        for anchor in by_class[physical]:
            candidates = []
            for method in methods:
                pcs = [x['pc'] for x in method['lines'] if x['sourceLine'] == anchor['sourceLine']]
                if pcs:
                    candidates.append(dict(name=method['name'], descriptor=method['descriptor'], pcs=pcs))
            rows.append(dict(**anchor, sourceSha256=normal['begin']['inputHashes'][source_path],
                             classSha256=expected_hash, jarModule=module,
                             jvmMethodCandidates=candidates,
                             jvmDisposition='EXACT_CLASS_LINE_TABLE_CANDIDATES' if candidates
                             else 'NO_EXACT_LINE_TABLE_MATCH_REQUIRES_FURTHER_RECONCILIATION'))
        classes.append(dict(physical=physical, sourcePath=source_path,
                            classSha256=expected_hash, jarModule=module, methods=methods))
    assert len(rows) == 76
    assert sum(x['missedBranches'] for x in rows) == 0
    for path in {x['path'] for x in anchors}:
        assert sha(ROOT / path) == normal['begin']['inputHashes'][path]
    for jar in jars.values():
        assert sha(Path(jar['path'])) == jar['sha256']
    write(OUT / 'class-line-map.json', dict(classes=classes, rows=rows))
    value = dict(actualExit=0, source=normal['source'],
                 normalManifestSha256=sha(normal_path), sourceFiles=21,
                 physicalClasses=37, lineAnchors=76,
                 reusedOriginalClasses=1, newJavapInvocations=36,
                 exactMatchAnchors=sum(bool(x['jvmMethodCandidates']) for x in rows),
                 ambiguousCandidateAnchors=sum(len(x['jvmMethodCandidates']) > 1 for x in rows),
                 classLineMapSha256=sha(OUT / 'class-line-map.json'),
                 jars=jars, stages=stages, targetClassesLoaded=False,
                 productExecution=False, oldExecRead=False, newProductPT=0,
                 coverageAdded=0, newAcceptance=0, formalUpdated=False,
                 scriptSha256=sha(Path(__file__)))
    write(OUT / 'manifest.json', value)
    print(json.dumps({k: value[k] for k in [
        'actualExit', 'sourceFiles', 'physicalClasses', 'lineAnchors',
        'exactMatchAnchors', 'ambiguousCandidateAnchors', 'newProductPT']}))


if __name__ == '__main__':
    try:
        if sys.argv[1:] == ['--line-tables-only']:
            missing_line_tables()
        elif not sys.argv[1:]:
            raise ValueError('historical declaration-only entrypoint disabled; explicit line-table mode required')
        else:
            raise ValueError('unsupported metadata mode')
    except Exception as failure:
        if OUT.is_dir() and not (OUT / 'manifest.json').exists():
            write(OUT / 'manifest.json', dict(actualExit=1,
                  phase='TOOL_OR_POSTCONDITION_FAILURE', errorType=type(failure).__name__,
                  newProductPT=0, coverageAdded=0, newAcceptance=0))
        raise
