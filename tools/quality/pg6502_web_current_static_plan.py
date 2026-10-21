"""Strict unchanged-source/class reauthentication; changed Web12 need fresh semantic review."""
import json
import os
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6500_web_owned_component_qualification_v5 import original_source
from pg6124_current3988_static_join import strict_pending
from static_disposition_overlay import load, validate_rationales

OLD = 'bbbc3f7f13b6858535515dc495ad53839683fb24'
PRIOR = BASE/'PG6462-current4056-static-join-v1/manifest.json'
PRIOR_SHA = '161554a8d1f964091bcc18fdaf2ac43ab0d1dbb0f1ddf4e38313ea0745a2c888'
QSHA = '67be969bc999b8cc5cd020faea6f1604bf8c32ebf8673f6db4a13910a8e90722'


def inputs():
    source = original_source()
    qp = BASE/'PG6500-web-owned-component-qualification-v5/manifest.json'
    if QSHA is None or sha(qp) != QSHA:
        raise ValueError('genuine current27 qualification before reauthentication')
    q = json.loads(qp.read_bytes()); pp = W/'pg6500-web-owned-component-qualification-v5/manifest.safe.json'
    rp = pp.with_name('findings.safe.json')
    if sha(pp) != q['privateManifestSha256'] or sha(rp) != q['findingsSha256']:
        raise ValueError('immutable original all-source/classes and raw PMD bytes')
    proof, raw = [json.loads(p.read_bytes()) for p in (pp, rp)]
    if (proof['source'] != source or proof['actualExit'] != 0 or proof['pmdRawFindings'] != 1361
            or proof['pmdProcessingErrors'] or proof['checkstyleFindings'] or proof['originalSixSpotBugs']):
        raise ValueError('complete raw1361/CS0/processing0/six0; no literal warning left')
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != proof['allSourceHashes']:
        raise ValueError('all851 current Main fixed')
    oldq = BASE/'PG6452-current4056-cases/qualification.json'
    if sha(oldq) != 'bddf967441ed173d5a9e89287c0d3b9916b9afcc07d15510d4f38878b63c5124':
        raise ValueError('immutable original4056 physical map')
    old = load(PRIOR, PRIOR_SHA, OLD)
    return source, old, json.loads(oldq.read_bytes())['allPhysicalMainSha256'], raw, proof, pp


def calculate():
    source, old, before, raw, proof, pp = inputs()
    rows, priors = strict_pending(old, before, raw, proof['allPhysicalMainSha256'])
    counts = Counter(r['status'] for r in rows)
    if counts != Counter(SOURCE_REBOUND_CURRENT_WHOLE_PENDING=1338, NOT_REVIEWED_CURRENT_SOURCE=23):
        raise ValueError('exact1338 unchanged/12 changed Web/11 held unresolved; no old semantic success import')
    unreviewed = [r for r in rows if r['status'] == 'NOT_REVIEWED_CURRENT_SOURCE']
    if sum(r['sourcePath'].endswith('/WebNativeRuntime.java') for r in unreviewed) != 12:
        raise ValueError('all twelve changed Web spans require fresh review, not prior missing-case promotion')
    for row in rows:
        if row['status'] == 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING':
            row.update(priorReviewSource=OLD, priorReviewManifestSha256=PRIOR_SHA,
                currentPhysicalProofSha256=sha(pp), formalAccepted=False, F03Accepted=False)
    validate_rationales(rows)
    return rows, dict(actualExit=0, source=source, rawFindings=1361, inventoryFile='findings.json',
        statusCounts=dict(counts), priorManifestPath=PRIOR.relative_to(ROOT).as_posix(), priorManifestSha256=PRIOR_SHA,
        originalSelectedQualificationSha256=QSHA, strictReboundPriorDecided=len(priors),
        changedWebFreshReviewRequired=12, heldOtherUnreviewed=11, oldPendingSuccessImported=False,
        currentWholeJoinPending=True, testsExecuted=0, additionalBuildsIssued=0, pmdRawRemoved=0,
        newAcceptedLeaves=0, formalAccepted=False, F03Accepted=False, ptAlternativeCompleted=0, effortPercent=None)


def main():
    rows, value = calculate(); os.umask(0o077)
    out = BASE/'PG6502-current4064-static-plan-v1'; out.mkdir()
    with (out/'findings.json').open('x') as f:
        json.dump(rows, f, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value['inventorySha256'] = sha(out/'findings.json')
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=value['source'], statusCounts=value['statusCounts'], manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__': main()
