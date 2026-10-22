"""Actual original whole counter differences only; no synthetic branch/old PASS splice."""
import hashlib
import json
import os
from pg5940_private_lock_compile import ROOT, BASE, sha
from pg6818_current_counter_delta import closed, counters, KINDS
from pg6092_current3985_static_join import source_case_candidates
from pg6932_original4222_artifacts import read_whole

BEFORE = BASE / 'PG6890-current4213-cases/qualification.json'
BEFORE_SHA = '80ad328f6e4f20d2f53f0e6ac4c314c1f698842a7b9b031b14d47592d19123ce'
TARGETS = {'batch:dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Receipt.class',
 'batch:dev/codex/schubert/nk/batch/file/RootServiceFacts$Facts.class',
 'batch:dev/codex/schubert/nk/batch/file/MorningBrokerExecution$Observations.class'}


def compare(before, after):
    if len(before['allPhysicalMainSha256']) != 1669 or before['allPhysicalMainSha256'] != after['allPhysicalMainSha256']:
        raise ValueError('all1669 physical Main exactly fixed')
    a, b = before['allActualClassCounters'], after['allActualClassCounters']
    if set(a) != set(b) or closed(before) - closed(after):
        raise ValueError('same actual class set and no lost four-positive closure')
    changed = [dict(physicalClass=k, before=a[k], after=b[k]) for k in sorted(a) if a[k] != b[k]]
    if not {r['physicalClass'] for r in changed} <= TARGETS:
        raise ValueError('unrelated counter differences require explicit classification')
    for row in changed:
        if set(row['before']) != set(row['after']):
            raise ValueError('no invented/removed counter applicability')
        for kind in row['before']:
            old, new = row['before'][kind], row['after'][kind]
            if old['missed'] < new['missed'] or sum(old.values()) != sum(new.values()):
                raise ValueError('no increased miss or changed denominator on fixed Main')
    return dict(explicitFourClosedBefore=len(closed(before)), explicitFourClosedAfter=len(closed(after)),
      newlyClosedClasses=sorted(closed(after) - closed(before)), reopenedClasses=[], changedCounters=changed,
      moduleCountersBefore=counters(before), moduleCountersAfter=counters(after), changedPhysicalMain=[])


def test_id_trace(cases):
    mapping = {
     'LegacyReceiptValueTest': {'retdata001LegacyZeroDoesNotManufactureTypedOrStoppedReceipt': 'PT-OPS-RETDATA-001'},
     'ObservationValueRedactionTest': {
      'obsdata001FactsRetainPublicInputsButDiagnosticNeverRendersYamlOrBinding': 'PT-OPS-OBSDATA-001',
      'obsdata002BrokerWrapperRetainsImmutablePublicDataButDiagnosticHasNoNestedDetails': 'PT-OPS-OBSDATA-002'}}
    for short, prefix in (('ApiLogFixtureOwnershipTest', 'A'), ('BatchFixtureOwnershipTest', 'B')):
        mapping[short] = {
         'dbfix1633001MissingConfigurationCreatesNoExternalOwner': 'PT-DBFIX-1633-' + prefix + '01',
         'dbfix1633002KnownStartedSetupSqlFailureCannotLeaveUnpublishedOwner': 'PT-DBFIX-1633-' + prefix + '02',
         'dbfix1633003NormalRoleAllTwentyFourTablesAndExplicitStopStayOwned': 'PT-DBFIX-1633-' + prefix + '03'}
    result = []
    for short, methods in mapping.items():
        paths = list(ROOT.glob('src/*/src/test/java/**/' + short + '.java'))
        if len(paths) != 1:
            raise ValueError('one independent Test source')
        path = paths[0]
        cls = path.as_posix().split('/src/test/java/')[1][:-5].replace('/', '.')
        for method, tid in methods.items():
            digest = hashlib.sha256(source_case_candidates(path.read_text(), method)[0].encode()).hexdigest()
            matches = [c for c in cases if c['class'] == cls and c['caseNameSha256'] == digest]
            if len(matches) != 1:
                raise ValueError('one original full XML case per fixed TestID')
            result.append(dict(testId=tid, sourcePath=path.relative_to(ROOT).as_posix(), sourceSha256=sha(path), method=method, originalCase=matches[0]))
    if len(result) != 9:
        raise ValueError('nine new method identities, never fixture vector count')
    return result


def main():
    qp, q, cases = read_whole()
    if sha(BEFORE) != BEFORE_SHA:
        raise ValueError('fixed original4213 identity and measured counter map')
    before = json.loads(BEFORE.read_bytes())
    if (before['tests'], q['tests']) != (4213, 4222) or before['allSourceHashes'] != q['allSourceHashes']:
        raise ValueError('two genuine full results, all851 Main unchanged')
    value = dict(actualExit=0, source=q['productionSource'], currentQualificationSha256=sha(qp), priorQualificationSha256=BEFORE_SHA,
      **compare(before, q), independentTestIdTrace=test_id_trace(cases), testsExecuted=0, wholeReplayed=False,
      formalAccepted=False, acceptedLeafDelta=0, effortPercent=None, ptAlternativeCompleted=0, vmActions=0,
      all851MainByteExact=True, physicalClassDenominator=1669, absentCounterSynthesized=False,
      toolSha256=sha(ROOT / 'tools/quality/pg6940_current4222_delta.py'))
    out = BASE / 'PG6940-current4222-delta-v1'
    os.umask(0o077)
    out.mkdir()
    path = out / 'manifest.json'
    with path.open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, manifestSha256=sha(path), closedBefore=value['explicitFourClosedBefore'], closedAfter=value['explicitFourClosedAfter'], remaining={t: value['moduleCountersAfter'][t]['missed'] for t in KINDS})))


if __name__ == '__main__':
    main()
