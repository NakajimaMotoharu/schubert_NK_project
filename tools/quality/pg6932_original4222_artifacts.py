"""Read only one original4222 whole; old cases are identities, never imported PASS."""
import hashlib
import inspect
import json
import subprocess
import tarfile
from pathlib import PurePosixPath
import pg6892_original4213_artifacts as previous
import pg6930_fixture4222_whole as whole
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg5966_api_sql_selected import ordinary_names
from pg6092_current3985_static_join import source_case_candidates


def emitted(data_hash, remote):
    raw = previous.emitted(data_hash, remote)
    anchor = "('PG6890', (4213, 656, 1669), 0))"
    if raw.count(anchor) != 1 or raw.count("'PG6890')") != 1:
        raise ValueError('one exact new original campaign binding')
    raw = raw.replace(anchor, "('PG6890', (4213, 656, 1669), 0), ('PG6930', (4222, 660, 1669), 0))", 1)
    raw = raw.replace("'PG6890')", "'PG6890', 'PG6930')", 1)
    compile(raw, '<original4222 export>', 'exec')
    return raw


def collect(*args, **kwargs):
    reader = previous.previous.reader
    raw = inspect.getsource(reader.collect)
    if raw.count("'PG6490')") != 1:
        raise ValueError('one original coverage guard')
    scope = {**vars(reader), 'emitted': emitted}
    exec(compile(raw.replace("'PG6490')", "'PG6490', 'PG6862', 'PG6890', 'PG6930')", 1), '<original4222 collector>', 'exec'), scope)
    return scope['collect'](*args, **kwargs)


def added_cases(source):
    whole.guard(source)
    rows = []
    for path in sorted(whole.NEW_TESTS):
        text = subprocess.check_output(['git', 'show', source + ':' + path], cwd=ROOT, text=True)
        rows.extend(dict(module=path.split('/')[1].removeprefix('schubert-nk-'),
          **{'class': path.split('/src/test/java/')[1][:-5].replace('/', '.')},
          caseNameSha256=hashlib.sha256(source_case_candidates(text, n)[0].encode()).hexdigest()) for n in ordinary_names(text))
    if len(rows) != 9:
        raise ValueError('nine independently declared methods, not vectors or selected-sum')
    return rows


def main():
    source = whole.original_source()
    run = W / whole.SLOT
    op = run / 'manifest.safe.json'
    original = json.loads(op.read_bytes())
    if not (original['source'] == source and original['actualExit'] == 0 and original['result']['run'] == 'PG6930-six-v1'
      and original['result']['productionSource'] == original['result']['sourceSnapshotHead'] == source):
        raise ValueError('genuine original4222 terminal first')
    if subprocess.check_output(['git', 'diff', source, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('original Main/Test/gates fixed')
    begin = json.loads((run / 'begin.safe.json').read_bytes())
    archive = run / 'source.tar'
    if sha(archive) != begin['archiveSha256']:
        raise ValueError('original archive exact')
    inputs = {}
    with tarfile.open(archive) as tar:
        for item in tar:
            if item.isdir():
                continue
            p = PurePosixPath(item.name)
            if not item.isfile() or p.is_absolute() or '..' in p.parts or item.name in inputs:
                raise ValueError('unique regular source archive')
            inputs[item.name] = hashlib.sha256(tar.extractfile(item).read()).hexdigest()
    oldq = BASE / 'PG6890-current4213-cases/qualification.json'
    cp = oldq.with_name('cases.json')
    if sha(oldq) != '80ad328f6e4f20d2f53f0e6ac4c314c1f698842a7b9b031b14d47592d19123ce' or sha(cp) != '9dbae51345642191cbfaa1f2132bb066c9614184e09e771cfe3f9e50accc0b6d':
        raise ValueError('frozen old4213 identity map, not success import')
    expected = [{k: r[k] for k in ('module', 'class', 'caseNameSha256')} for r in json.loads(cp.read_bytes())] + added_cases(source)
    qp = BASE / 'PG6928-db-fixture-green-original-v1/manifest.json'
    pp = W / 'pg6928-db-fixture-green-original-v1/manifest.safe.json'
    q = json.loads(qp.read_bytes())
    if whole.QSHA is None or sha(qp) != whole.QSHA or not (q['source'] == source and q['actualExit'] == 0
      and (q['tests'], q['suites'], q['physicalMain']) == (21, 10, 1669) and sha(pp) == q['privateManifestSha256']):
        raise ValueError('same-source originalgreen21 first')
    proof = json.loads(pp.read_bytes())
    main_inputs = previous.previous.reader.production_source_inputs(inputs)
    old = json.loads(oldq.read_bytes())
    if len(main_inputs) != 851 or main_inputs != proof['allSourceHashes'] or main_inputs != old['allSourceHashes'] or proof['allPhysicalMainSha256'] != old['allPhysicalMainSha256']:
        raise ValueError('all851/1669 unchanged; old Test-only success not copied')
    payload = dict(source=source, campaign='PG6930', expectedCounts=[4222, 660, 1669], returnedOriginalResult=original['result'],
      archiveSha256=begin['archiveSha256'], allSourceInputs=inputs, expectedMainSourceInputs=main_inputs, expectedCases=expected,
      priorFullMain=old['allPhysicalMainSha256'], changedOwnerKeys=[], physicalExpectedCounts=[1669, 1669],
      physicalExpectedAdded=[], expectedCurrentMain=proof['allPhysicalMainSha256'], includeCoverageXml=True)
    return collect(payload, op, 'pg6932-original4222-artifacts-v1', '/home/mini/schubert-nk-pgpt/transfer/PG6932-original4222-v1', 'PG6930-current4222-cases')


def read_whole():
    raw = inspect.getsource(previous.previous.read_whole)
    for before, after in (('PG6862-current4209-cases', 'PG6930-current4222-cases'),
      ('pg6864-original4209-artifacts-v1', 'pg6932-original4222-artifacts-v1'), ('4209', '4222'), ('653', '660')):
        raw = raw.replace(before, after)
    scope = {**vars(previous.previous), 'whole': whole}
    exec(compile(raw, '<original4222 reader>', 'exec'), scope)
    return scope['read_whole']()


if __name__ == '__main__':
    main()
