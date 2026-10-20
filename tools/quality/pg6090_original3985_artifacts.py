"""Read the original integrated3985 after genuine terminal; no extra test or runtime operation."""
import hashlib
import json
import subprocess
import tarfile
from pathlib import PurePosixPath
import pg6042_original3976_artifacts as reader
from pg5940_private_lock_compile import sha
from pg6082_web_factory_qualification import SOURCE
from pg6074_jms_owner_selected import MAIN as PREPARED_MAIN, TESTS
from pg6080_web_factory_selected import MAIN as PROVIDER_MAIN, TEST as PROVIDER_TEST
from pg5966_api_sql_selected import ordinary_names, source_test_names

ROOT, W, BASE = reader.ROOT, reader.W, reader.BASE
OLD = 'c4d0242abe53fa7916451ac22caffcdfc13d82b6'


def new_case_identities():
    added = []
    for path in sorted(TESTS):
        old = subprocess.check_output(['git', 'show', OLD+':'+path], cwd=ROOT, text=True)
        text = (ROOT/path).read_text()
        marker = 'class '+path.rsplit('/', 1)[1][:-5]+' {\n'
        if old.count(marker) != 1:
            raise ValueError('one exact Test class declaration')
        start = old.index(marker)+len(marker)
        prefix, suffix = old[:start], old[start:]
        if path.endswith('/WebLogConsumersTest.java'):
            prefix = prefix.replace('import static org.junit.jupiter.api.Assertions.assertNull;\n',
                                    'import static org.junit.jupiter.api.Assertions.assertNull;\nimport static org.junit.jupiter.api.Assertions.assertSame;\n', 1)
        if not text.startswith(prefix) or not text.endswith(suffix):
            raise ValueError('all original Test bodies/fixtures byte-identical;only explicit new leading Test and one assertion import')
        insert = text[len(prefix):-len(suffix)]
        names = ordinary_names(insert)
        if len(names) != 1 or any(not name.startswith('jmsown00') for name in names):
            raise ValueError('one independent acquisition boundary Test before original tests')
        if ordinary_names(text) != ordinary_names(old) | names:
            raise ValueError('exact old/new source case names,no expected PASS import')
        module = path.split('/')[1].removeprefix('schubert-nk-')
        cls = path.split('/src/test/java/')[1][:-5].replace('/', '.')
        added += [dict(module=module, **{'class': cls}, caseNameSha256=hashlib.sha256(n.encode()).hexdigest()) for n in names]
    names = source_test_names(ROOT/PROVIDER_TEST)
    if len(names) != 3 or any(not n.startswith('mqfact31100') for n in names):
        raise ValueError('three independent provider Test identities')
    cls = PROVIDER_TEST.split('/src/test/java/')[1][:-5].replace('/', '.')
    added += [dict(module='web', **{'class': cls}, caseNameSha256=hashlib.sha256(n.encode()).hexdigest()) for n in sorted(names)]
    if len(added) != 6:
        raise ValueError('exact six new source-declared identities,not six assumed successes')
    return added


def main():
    original_path = W/'pg6088-jms-owner-six-v1/manifest.safe.json'
    original = json.loads(original_path.read_bytes())
    if not (original['source'] == SOURCE and original['actualExit'] == 0 and original['result']['run'] == 'PG6088-six-v1'
            and original['result']['productionSource'] == original['result']['sourceSnapshotHead'] == SOURCE):
        raise ValueError('original current3985 genuine terminal before reader')
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('canonical source/Test/gates remain fixed')
    owners = PREPARED_MAIN | {PROVIDER_MAIN}
    changed = set(subprocess.check_output(['git', 'diff', '--name-only', OLD, SOURCE, '--', 'src'], cwd=ROOT, text=True).splitlines())
    if changed != owners | TESTS | {PROVIDER_TEST} or len(owners) != 5:
        raise ValueError('only five Main/four Test sources')
    begin = json.loads((W/'pg6088-jms-owner-six-v1/begin.safe.json').read_bytes())
    archive = W/'pg6088-jms-owner-six-v1/source.tar'
    if sha(archive) != begin['archiveSha256']:
        raise ValueError('original fixed source archive')
    inputs = {}
    with tarfile.open(archive) as tar:
        for member in tar:
            if member.isdir():
                continue
            name = PurePosixPath(member.name)
            if not member.isfile() or name.is_absolute() or '..' in name.parts or member.name in inputs:
                raise ValueError('all unique regular archived inputs')
            inputs[member.name] = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    oldq = BASE/'PG6060-current3979-cases/qualification.json'; oldcases = oldq.with_name('cases.json')
    if sha(oldq) != '4a411f7710e793e34204cc738d7882c69d500967b719c596c48687e195b84a5e' or sha(oldcases) != 'b4f4fb0d819b59fa971f8795793a9e5d061ef542c1a4d9c2cb3b4acfa6155c03':
        raise ValueError('historical physical and semantic case identities immutable,not PASS transfer')
    expected = [{k: r[k] for k in ('module', 'class', 'caseNameSha256')} for r in json.loads(oldcases.read_bytes())]
    expected += new_case_identities()
    qp = BASE/'PG6082-web-factory-qualification-v1/manifest.json'; private = W/'pg6082-web-factory-qualification-v1/manifest.safe.json'
    if sha(qp) != '134e8181764a40b725fd0fa9365f5d18fa714b66221e4f46b992d3f84cd7e735':
        raise ValueError('actual current925 physical/source qualification')
    q = json.loads(qp.read_bytes())
    if sha(private) != q['privateManifestSha256']:
        raise ValueError('qualified original private source/class map hash')
    proof = json.loads(private.read_bytes()); main_inputs = reader.production_source_inputs(inputs)
    if main_inputs != proof['allSourceHashes'] or len(main_inputs) != 851 or proof['source'] != SOURCE:
        raise ValueError('all851 same current Main source in original whole archive')
    owner_keys = sorted(p.split('/')[1].removeprefix('schubert-nk-')+':'+p.split('/src/main/java/')[1][:-5]+'.class' for p in owners)
    data = dict(source=SOURCE, campaign='PG6088', expectedCounts=[3985, 595, 1667],
        returnedOriginalResult=original['result'], archiveSha256=begin['archiveSha256'], allSourceInputs=inputs,
        expectedMainSourceInputs=main_inputs, expectedCases=expected,
        priorFullMain=json.loads(oldq.read_bytes())['allPhysicalMainSha256'], changedOwnerKeys=owner_keys,
        physicalExpectedCounts=[1667, 1667], physicalExpectedAdded=[], expectedCurrentMain=proof['allPhysicalMainSha256'],
        includeCoverageXml=True)
    return reader.collect(data, original_path, 'pg6090-original3985-artifacts-v1',
        '/home/mini/schubert-nk-pgpt/transfer/PG6090-original3985-v1', 'PG6088-current3985-cases')


if __name__ == '__main__':
    main()
