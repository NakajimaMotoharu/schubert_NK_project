"""Compare only two original whole measurements; Test-only source, no coverage synthesis."""
import hashlib
import json
import os
from pg5940_private_lock_compile import ROOT, BASE, sha
from pg6818_current_counter_delta import closed, counters, KINDS
from pg6092_current3985_static_join import source_case_candidates
from pg6892_original4213_artifacts import read_whole

BEFORE = BASE / 'PG6862-current4209-cases/qualification.json'
BEFORE_SHA = '5aa628fcb1119757f6eb030eac68cf6cc851105ce014eb2b9ad0506b4925ce85'
ROOTCTX = 'batch:dev/codex/schubert/nk/batch/platform/RootStartupContext.class'
GATE = 'batch:dev/codex/schubert/nk/batch/file/MorningGateEvidence.class'
OBSERVED = 'batch:dev/codex/schubert/nk/batch/file/RootCurrentPermitPreflight$Observed.class'


def compare(before, after):
    if len(before['allPhysicalMainSha256']) != 1669 or before['allPhysicalMainSha256'] != after['allPhysicalMainSha256']:
        raise ValueError('Test-only all1669 physical Main exact')
    if closed(after) - closed(before) != {ROOTCTX, GATE} or closed(before) - closed(after):
        raise ValueError('only two expected newly four-closed and none reopened')
    a, b = before['allActualClassCounters'], after['allActualClassCounters']
    if set(a) != set(b):
        raise ValueError('same actual XML class set; no absent-counter filling')
    changed = [dict(physicalClass=k, before=a[k], after=b[k]) for k in sorted(a) if a[k] != b[k]]
    if {r['physicalClass'] for r in changed} != {ROOTCTX, GATE, OBSERVED}:
        raise ValueError('unrelated changed counter needs its own classification')
    for row in changed:
        if set(row['before']) != set(row['after']):
            raise ValueError('counter applicability unchanged')
        for kind in row['before']:
            old, new = row['before'][kind], row['after'][kind]
            if old['missed'] < new['missed'] or sum(old.values()) != sum(new.values()):
                raise ValueError('no lost coverage or total-counter change with identical Main')
    return dict(explicitFourClosedBefore=len(closed(before)), explicitFourClosedAfter=len(closed(after)),
      newlyClosedClasses=sorted(closed(after) - closed(before)), reopenedClasses=[], changedCounters=changed,
      moduleCountersBefore=counters(before), moduleCountersAfter=counters(after), changedPhysicalMain=[])


def test_id_trace(cases):
    mapping = {
     'batch/file/RetentionWireBoundaryTest': {
      'retwire001DeletedGenerationWholeFrameAndDiskPostconditions': 'PT-OPS-RETWIRE-001',
      'retwire002InjectedName255Accepted256RejectedWithoutFilesystemNameCreation': 'PT-OPS-RETWIRE-002'},
     'batch/file/CurrentObservationValueTest': {'data511001WrapperRetainsValuesButNeverPrintsPublicBindings': 'PT-OPS-DATA-511001'},
     'batch/platform/ServiceDeadlineArgumentTest': {'data511002UnsupportedActorAndNonpositiveBudgetRefuseBeforeAllIo': 'PT-OPS-DATA-511002'}}
    result = []
    for name, methods in mapping.items():
        path = ROOT / ('src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/' + name + '.java')
        cls = 'dev.codex.schubert.nk.' + name.replace('/', '.')
        for method, tid in methods.items():
            digest = hashlib.sha256(source_case_candidates(path.read_text(), method)[0].encode()).hexdigest()
            matches = [c for c in cases if c['class'] == cls and c['caseNameSha256'] == digest]
            if len(matches) != 1:
                raise ValueError('one original full XML case per independent TestID')
            result.append(dict(testId=tid, sourcePath=path.relative_to(ROOT).as_posix(), sourceSha256=sha(path), method=method, originalCase=matches[0]))
    if len(result) != 4:
        raise ValueError('four JUnit methods, no vector count')
    return result


def main():
    qp, q, cases = read_whole()
    if sha(BEFORE) != BEFORE_SHA:
        raise ValueError('fixed original4209')
    before = json.loads(BEFORE.read_bytes())
    if (before['tests'], q['tests']) != (4209, 4213) or before['allSourceHashes'] != q['allSourceHashes']:
        raise ValueError('two original full results/all851 Main unchanged')
    value = dict(actualExit=0, source=q['productionSource'], currentQualificationSha256=sha(qp), priorQualificationSha256=BEFORE_SHA,
      **compare(before, q), independentTestIdTrace=test_id_trace(cases), testsExecuted=0, wholeReplayed=False,
      formalAccepted=False, acceptedLeafDelta=0, effortPercent=None, ptAlternativeCompleted=0, vmActions=0,
      all851MainByteExact=True, physicalClassDenominator=1669, absentCounterSynthesized=False,
      toolSha256=sha(ROOT / 'tools/quality/pg6900_current4213_delta.py'))
    out = BASE / 'PG6900-current4213-delta-v1'
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
