"""After genuine original6060 terminal0 only: inspect original artifacts,no new PT or runtime action."""
import hashlib
import json
import subprocess
import tarfile
from pathlib import PurePosixPath
import pg6042_original3976_artifacts as reader
from pg6054_expiry_read_qualification import SOURCE, MAIN
from pg6052_expiry_combined_selected import TEST, OLD_TEST
from pg5966_api_sql_selected import source_test_names

ROOT, W, BASE = reader.ROOT, reader.W, reader.BASE
NEW_CLASS = 'dev.codex.schubert.nk.batch.repository.ExpiryAuditResourceFailureTest'
NEW_METHODS = {'primaryErrorSurvivesSqlCloseExactlyOnce',
    'independent68CompoundFailuresPreserveTypedPriorityAndBorrowedConnection',
    'normalEmptySnapshotMandatoryNullAndProviderUnknownRemainDistinct'}


def main():
    original_path = W/'pg6060-expiry-six-v1/manifest.safe.json'
    original = json.loads(original_path.read_bytes())
    if not (original['source'] == SOURCE and original['actualExit'] == 0 and original['result']['run'] == 'PG6060-six-v1'
            and original['result']['productionSource'] == original['result']['sourceSnapshotHead'] == SOURCE):
        raise ValueError('genuine original3979 terminal0,canonical sourceSnapshot not metadata operator')
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('canonical Main/Test/gates remain fixed')
    prior = '8c869d7cea21d587b859b3e72e3516d9d2deb5c8'
    actual_changes = set(subprocess.check_output(['git', 'diff', '--name-only', prior, SOURCE, '--', 'src'], cwd=ROOT, text=True).splitlines())
    if actual_changes != {MAIN, TEST, OLD_TEST} or source_test_names(ROOT/TEST) != NEW_METHODS:
        raise ValueError('exact localized Main/new3/approved BAT287 oracle correction only')
    begin = json.loads((W/'pg6060-expiry-six-v1/begin.safe.json').read_bytes()); archive = W/'pg6060-expiry-six-v1/source.tar'
    if reader.hashlib.sha256(archive.read_bytes()).hexdigest() != begin['archiveSha256']:
        raise ValueError('original archive identity')
    inputs = {}
    with tarfile.open(archive) as tar:
        for member in tar:
            if member.isdir():
                continue
            name = PurePosixPath(member.name)
            if not member.isfile() or name.is_absolute() or '..' in name.parts or member.name in inputs:
                raise ValueError('all unique regular source archive inputs retained')
            inputs[member.name] = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    oldq = BASE/'PG6040-current3976-cases/qualification.json'; oldcases = oldq.with_name('cases.json')
    if reader.hashlib.sha256(oldq.read_bytes()).hexdigest() != '0d11101550922d207fec3ba3f1d2fa9bbb3b35a5b5fabfc83cdb35a6ea950788' or reader.hashlib.sha256(oldcases.read_bytes()).hexdigest() != 'af2845e1a6c82581975e6a3362db9392696092542467040236d73212736528f1':
        raise ValueError('immutable prior physical/case identity set,not imported PASS')
    expected = [{k: r[k] for k in ('module', 'class', 'caseNameSha256')} for r in json.loads(oldcases.read_bytes())]
    expected += [dict(module='batch', **{'class': NEW_CLASS}, caseNameSha256=hashlib.sha256(n.encode()).hexdigest()) for n in sorted(NEW_METHODS)]
    current = W/'pg6054-expiry-read-qualification-v1/manifest.safe.json'
    if hashlib.sha256(current.read_bytes()).hexdigest() != '14128e3496c796aca15bb9bd8bc46d87a2662a34e8f412125d1b667ff029c885':
        raise ValueError('current selected Main physical proof immutable')
    qualified = json.loads(current.read_bytes()); main_inputs = reader.production_source_inputs(inputs)
    if main_inputs != qualified['allSourceHashes'] or len(main_inputs) != 851 or qualified['source'] != SOURCE:
        raise ValueError('all851 actual current source equals original whole archive')
    owner = 'batch:'+MAIN.split('/src/main/java/')[1][:-5]+'.class'
    data = dict(source=SOURCE, campaign='PG6060', expectedCounts=[3979, 594, 1667],
        returnedOriginalResult=original['result'], archiveSha256=begin['archiveSha256'], allSourceInputs=inputs,
        expectedMainSourceInputs=main_inputs, expectedCases=expected,
        priorFullMain=json.loads(oldq.read_bytes())['allPhysicalMainSha256'], changedOwnerKeys=[owner],
        physicalExpectedCounts=[1667, 1667], physicalExpectedAdded=[], expectedCurrentMain=qualified['allPhysicalMainSha256'])
    return reader.collect(data, original_path, 'pg6066-original3979-artifacts-v1',
        '/home/mini/schubert-nk-pgpt/transfer/PG6066-original3979-v1', 'PG6060-current3979-cases')


if __name__ == '__main__':
    main()
