"""Read one original4213 job; old cases provide identity only, never imported PASS/coverage."""
import hashlib
import inspect
import json
import subprocess
import tarfile
from pathlib import PurePosixPath
import pg6864_original4209_artifacts as previous
import pg6890_data4213_whole as whole
import pg6884_data_boundary_selected as selected
import pg6878_retention_wire_selected as retention
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg5966_api_sql_selected import ordinary_names
from pg6092_current3985_static_join import source_case_candidates


def unchanged_physical(before, after, owners, expected_counts=(1669, 1669), expected_added=None):
    if owners or tuple(expected_counts) != (1669, 1669) or expected_added != [] or len(before) != 1669 or before != after:
        raise ValueError('Test-only all1669 maps must be exactly equal, no owner/add/remove/change or alternate denominator')
    return [], [], 1669


def emitted(data_hash, remote):
    raw = previous.emitted(data_hash, remote)
    anchor = "('PG6862', (4209, 653, 1669), 1))"
    if raw.count(anchor) != 1 or raw.count("'PG6862')") != 1:
        raise ValueError('one original4213 dimension binding')
    raw = raw.replace(anchor, "('PG6862', (4209, 653, 1669), 1), ('PG6890', (4213, 656, 1669), 0))", 1).replace("'PG6862')", "'PG6862', 'PG6890')", 1)
    call = 'changed, added, unchanged = physical_difference('
    terminal = '\nprint(json.dumps(inspect_original(json.loads(p.read_bytes()))))'
    if raw.count(call) != 1 or raw.count(terminal) != 1:
        raise ValueError('one exact physical check and original terminal')
    raw = raw.replace(call, 'changed, added, unchanged = unchanged_physical(', 1)
    return raw.replace(terminal, '\n' + inspect.getsource(unchanged_physical) + terminal, 1)


def collect(*args, **kwargs):
    raw = inspect.getsource(previous.reader.collect)
    if raw.count("'PG6490')") != 1:
        raise ValueError('one original coverage collector guard')
    scope = {**vars(previous.reader), 'emitted': emitted}
    exec(compile(raw.replace("'PG6490')", "'PG6490', 'PG6862', 'PG6890')", 1), '<original4213 collector>', 'exec'), scope)
    return scope['collect'](*args, **kwargs)


def added_cases(source):
    selected.guard(source)
    tests = set(selected.TESTS) | {retention.TEST}
    changes = subprocess.check_output(['git', 'diff', '--name-status', retention.OLD, source, '--', ':(glob)src/*/src/test/java/**/*Test.java'], cwd=ROOT, text=True).splitlines()
    if set(changes) != {'A\t' + p for p in tests} or len(changes) != 3:
        raise ValueError('three new Test files; all old oracles fixed')
    if subprocess.check_output(['git', 'diff', retention.OLD, source, '--', ':(glob)src/*/src/main/**/*'], cwd=ROOT):
        raise ValueError('every Main unchanged')
    rows = []
    for path in sorted(tests):
        text = subprocess.check_output(['git', 'show', source + ':' + path], cwd=ROOT, text=True)
        for name in ordinary_names(text):
            rows.append(dict(module='batch', **{'class': path.split('/src/test/java/')[1][:-5].replace('/', '.')},
              caseNameSha256=hashlib.sha256(source_case_candidates(text, name)[0].encode()).hexdigest()))
    if len(rows) != 4:
        raise ValueError('four independent JUnit declarations, not vector count')
    return rows


def main():
    source = whole.original_source()
    run = W / whole.SLOT
    op = run / 'manifest.safe.json'
    o = json.loads(op.read_bytes())
    if not (o['source'] == source and o['actualExit'] == 0 and o['result']['run'] == 'PG6890-six-v1'
      and o['result']['productionSource'] == o['result']['sourceSnapshotHead'] == source):
        raise ValueError('genuine original4213 terminal first')
    if subprocess.check_output(['git', 'diff', source, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('original Main/Test/gates fixed')
    begin = json.loads((run / 'begin.safe.json').read_bytes())
    archive = run / 'source.tar'
    if sha(archive) != begin['archiveSha256']:
        raise ValueError('original archive identity')
    inputs = {}
    with tarfile.open(archive) as tar:
        for item in tar:
            if item.isdir():
                continue
            path = PurePosixPath(item.name)
            if not item.isfile() or path.is_absolute() or '..' in path.parts or item.name in inputs:
                raise ValueError('unique regular original input')
            inputs[item.name] = hashlib.sha256(tar.extractfile(item).read()).hexdigest()
    oldq = BASE / 'PG6862-current4209-cases/qualification.json'
    cp = oldq.with_name('cases.json')
    if sha(oldq) != '5aa628fcb1119757f6eb030eac68cf6cc851105ce014eb2b9ad0506b4925ce85' or sha(cp) != 'ade4bba609123fff39ef5fa4b757d67a001cadbb4bd181174060480c1a3f244b':
        raise ValueError('frozen old4209 identity map, not PASS import')
    expected = [{k: r[k] for k in ('module', 'class', 'caseNameSha256')} for r in json.loads(cp.read_bytes())] + added_cases(source)
    qp = BASE / 'PG6886-data-boundary-original-v1/manifest.json'
    pp = W / 'pg6886-data-boundary-original-v1/manifest.safe.json'
    q = json.loads(qp.read_bytes())
    if whole.QSHA is None or sha(qp) != whole.QSHA or not (q['source'] == source and q['actualExit'] == 0
      and (q['tests'], q['suites'], q['physicalMain']) == (42, 11, 1669) and sha(pp) == q['privateManifestSha256']):
        raise ValueError('same-source original42/all8511669')
    proof = json.loads(pp.read_bytes())
    main = previous.reader.production_source_inputs(inputs)
    old = json.loads(oldq.read_bytes())
    if len(main) != 851 or main != proof['allSourceHashes'] or main != old['allSourceHashes'] or proof['allPhysicalMainSha256'] != old['allPhysicalMainSha256']:
        raise ValueError('all851/1669 unchanged Main; old Test-only PASS not copied')
    payload = dict(source=source, campaign='PG6890', expectedCounts=[4213, 656, 1669], returnedOriginalResult=o['result'],
      archiveSha256=begin['archiveSha256'], allSourceInputs=inputs, expectedMainSourceInputs=main, expectedCases=expected,
      priorFullMain=old['allPhysicalMainSha256'], changedOwnerKeys=[], physicalExpectedCounts=[1669, 1669],
      physicalExpectedAdded=[], expectedCurrentMain=proof['allPhysicalMainSha256'], includeCoverageXml=True)
    return collect(payload, op, 'pg6892-original4213-artifacts-v1', '/home/mini/schubert-nk-pgpt/transfer/PG6892-original4213-v1', 'PG6890-current4213-cases')


def read_whole():
    raw = inspect.getsource(previous.read_whole)
    for before, after in (('PG6862-current4209-cases', 'PG6890-current4213-cases'), ('pg6864-original4209-artifacts-v1', 'pg6892-original4213-artifacts-v1'), ('4209', '4213'), ('653', '656')):
        raw = raw.replace(before, after)
    scope = {**vars(previous), 'whole': whole}
    exec(compile(raw, '<original4213 reader>', 'exec'), scope)
    return scope['read_whole']()


if __name__ == '__main__':
    main()
