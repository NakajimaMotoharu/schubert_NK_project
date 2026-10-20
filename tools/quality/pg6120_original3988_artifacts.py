"""Original3988 terminal/XML/Jar/coverage verification only; no new Maven or runtime action."""
import hashlib
import json
import subprocess
import tarfile
from pathlib import PurePosixPath
import pg6042_original3976_artifacts as reader
from pg5940_private_lock_compile import sha
from pg6114_http_owner_qualification import SOURCE
from pg6112_http_owner_selected import PATHS
from pg5966_api_sql_selected import ordinary_names
from pg6106_locked_flag_selected import MAIN as FLAG

ROOT, W, BASE = reader.ROOT, reader.W, reader.BASE
OLD = '870010d6681d74519237be7a7ca6381a190f471a'


def new_case_identities():
    added = []
    for path in sorted(p for p in PATHS if '/src/test/java/' in p):
        old = subprocess.check_output(['git', 'show', OLD+':'+path], cwd=ROOT, text=True)
        text = (ROOT/path).read_text()
        marker = 'class '+path.rsplit('/', 1)[1][:-5]+' {\n'
        if path.endswith('/WebHttpServerTest.java'):
            marker += '  @TempDir Path root;\n'
        if old.count(marker) != 1:
            raise ValueError('one explicit test insertion boundary')
        at = old.index(marker)+len(marker)
        prefix, suffix = old[:at], old[at:]
        if not text.startswith(prefix) or not text.endswith(suffix):
            raise ValueError('all existing Tests/fixtures/expected bytes preserved;only explicit leading Test added')
        names = ordinary_names(text[len(prefix):-len(suffix)])
        if len(names) != 1 or any(not name.startswith('httpOwn00') for name in names) or ordinary_names(text) != ordinary_names(old) | names:
            raise ValueError('one new HTTP acquisition Test identity per owner')
        module = path.split('/')[1].removeprefix('schubert-nk-')
        cls = path.split('/src/test/java/')[1][:-5].replace('/', '.')
        added += [dict(module=module, **{'class': cls}, caseNameSha256=hashlib.sha256(n.encode()).hexdigest()) for n in names]
    if len(added) != 3:
        raise ValueError('exact three declared identities,not assumed PASS arithmetic')
    return added


def main():
    original_path = W/'pg6118-http-owner-six-v1/manifest.safe.json'
    original = json.loads(original_path.read_bytes())
    if not (original['source'] == SOURCE and original['actualExit'] == 0 and original['result']['run'] == 'PG6118-six-v1'
            and original['result']['productionSource'] == original['result']['sourceSnapshotHead'] == SOURCE):
        raise ValueError('genuine current3988 terminal before reader')
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('canonical source/Test/gates fixed')
    owners = {p for p in PATHS if '/src/main/java/' in p} | {FLAG}
    changed = set(subprocess.check_output(['git', 'diff', '--name-only', OLD, SOURCE, '--', 'src'], cwd=ROOT, text=True).splitlines())
    if changed != PATHS | {FLAG} or len(owners) != 4:
        raise ValueError('only three HTTP Main+Tests and one locked flag')
    begin = json.loads((W/'pg6118-http-owner-six-v1/begin.safe.json').read_bytes())
    archive = W/'pg6118-http-owner-six-v1/source.tar'
    if sha(archive) != begin['archiveSha256']:
        raise ValueError('original source archive identity')
    inputs = {}
    with tarfile.open(archive) as tar:
        for member in tar:
            if member.isdir():
                continue
            path = PurePosixPath(member.name)
            if not member.isfile() or path.is_absolute() or '..' in path.parts or member.name in inputs:
                raise ValueError('unique regular original archive inputs')
            inputs[member.name] = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    oldq = BASE/'PG6088-current3985-cases/qualification.json'
    oldcases = oldq.with_name('cases.json')
    if sha(oldq) != '76d222eef92096c6b9fb84c73fb978836a441ec52ced506f0bdc3ece3d4f183a' or sha(oldcases) != '0ce3390f37aeabad4ecfef5f45a0ab7af6d8fb2f77d34ab955156ae5eaac9c90':
        raise ValueError('immutable prior case identities/physical map;not a PASS transfer')
    expected = [{k: row[k] for k in ('module', 'class', 'caseNameSha256')} for row in json.loads(oldcases.read_bytes())]
    expected += new_case_identities()
    qp = BASE/'PG6114-http-owner-qualification-v1/manifest.json'
    private = W/'pg6114-http-owner-qualification-v1/manifest.safe.json'
    q = json.loads(qp.read_bytes())
    if q['actualExit'] != 0 or q['source'] != SOURCE or (q['tests'], q['suites']) != (1939, 318) or sha(private) != q['privateManifestSha256']:
        raise ValueError('genuine current1939/318 source and physical qualification')
    proof = json.loads(private.read_bytes()); main_inputs = reader.production_source_inputs(inputs)
    if main_inputs != proof['allSourceHashes'] or len(main_inputs) != 851 or proof['source'] != SOURCE:
        raise ValueError('all851 current source in original whole archive')
    keys = sorted(p.split('/')[1].removeprefix('schubert-nk-')+':'+p.split('/src/main/java/')[1][:-5]+'.class' for p in owners)
    data = dict(source=SOURCE, campaign='PG6118', expectedCounts=[3988, 595, 1667],
                returnedOriginalResult=original['result'], archiveSha256=begin['archiveSha256'], allSourceInputs=inputs,
                expectedMainSourceInputs=main_inputs, expectedCases=expected,
                priorFullMain=json.loads(oldq.read_bytes())['allPhysicalMainSha256'], changedOwnerKeys=keys,
                physicalExpectedCounts=[1667, 1667], physicalExpectedAdded=[], expectedCurrentMain=proof['allPhysicalMainSha256'],
                includeCoverageXml=True)
    return reader.collect(data, original_path, 'pg6120-original3988-artifacts-v1',
                          '/home/mini/schubert-nk-pgpt/transfer/PG6120-original3988-v1', 'PG6118-current3988-cases')


if __name__ == '__main__':
    main()
