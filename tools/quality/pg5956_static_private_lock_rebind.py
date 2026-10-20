"""Strict byte-identical489 reasons only; changed56 explicitly held for re-review."""
import copy
import json
import os
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, OLD, plan, sha
from pg5944_private_lock_whole import SOURCE
from pg5910_storage_static_rebind import ordered_pairs
from pg5918_api_static_rebind import prior_disposition
from pg5758_static_rebind import bind_one
from static_disposition_overlay import load

PRIOR = BASE/'PG5934-current-static3973-v1/manifest.json'
PRIOR_SHA = '7b18bc543eaf7be827dd22c78aea321f1bf0bb996dbeedd92b83395b675bcbfb'


def main():
    before_rows = load(PRIOR, PRIOR_SHA, OLD)
    sp = BASE/'PG5942-private-lock-static-v1/manifest.json'; fp = sp.with_name('findings.json')
    if sha(sp) != 'fba315bab4168d6150638c7a21b5209dfce88b0f97951e456ed3d52d33edbda5' or sha(fp) != '7aed765f19608713c3c2d6d09e48faecdffa3f77c354b195b67af1c4abe0798a':
        raise ValueError('actual complete current raw1451')
    proofs = []
    for name, pub in (('pg5914-api-expression-static-v1', BASE/'PG5914-api-expression-static-v1/manifest.json'), ('pg5942-private-lock-static-v1', sp)):
        p = W/name/'manifest.safe.json'
        if sha(p) != json.loads(pub.read_bytes())['privateManifestSha256']:
            raise ValueError('actual all851/1666 source/class map proof')
        proofs.append(json.loads(p.read_bytes()))
    old, current = proofs
    if old['source'] != OLD or current['source'] != SOURCE or {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != current['allSourceHashes']:
        raise ValueError('actual current851 immutable source')
    raw = json.loads(fp.read_bytes()); pairs = ordered_pairs(before_rows, raw)
    decided = {r['findingId']: r for r in before_rows if r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE'}
    changed_paths = {r['path'] for r in plan()['sourcePlans']}; result = []; used = set()
    for row in raw:
        pair = pairs.get(row['findingId']); previous = decided.get(pair[0]['findingId']) if pair else None
        if row['sourcePath'] in changed_paths:
            result.append(copy.deepcopy(row)); continue
        value, kind = bind_one(row, [prior_disposition(previous)] if previous else [], (ROOT/row['sourcePath']).read_bytes(), old['auxClassHashes'], current['auxClassHashes'])
        if kind == 'REBOUND':
            used.add(previous['findingId'])
            # References now carry semantic identity only. Never import a previous PASS result.
            refs = [dict(klass=r['class'], **{'class': r['class']}, caseNameSha256=r['caseNameSha256']) for r in previous['currentWholeCaseRefs']]
            value.update(historicalCaseIds=[], plannedCurrentTestRefs=refs, priorReviewSource=OLD, priorReviewManifestSha256=PRIOR_SHA,
                         currentPhysicalProofSha256=sha(W/'pg5942-private-lock-static-v1/manifest.safe.json'),
                         priorFindingId=previous['findingId'], priorRawXmlOrdinal=previous['rawXmlOrdinal'],
                         sourceFileOccurrenceRank=pair[1], diagnosticIdentityMapping='EXACT_ENTIRE_SOURCE_DIAGNOSTIC_SEQUENCE_WITHIN_FILE', historicalPtImportedAsCurrent=False)
        result.append(value)
    held = [dict(findingId=k, sourcePath=decided[k]['sourcePath'], rule=decided[k]['rule'], reason='SOURCE/OWNER_CHANGED; explicit current re-review required') for k in sorted(set(decided)-used)]
    if len(result) != 1451 or len(used) != 489 or len(held) != 56 or any(r['sourcePath'] not in changed_paths for r in held):
        raise ValueError('only exact489 unchanged; changed56 held, all1451 retained')
    out = BASE/'PG5956-private-lock-dispositions-v1'; os.umask(0o077); out.mkdir(); fp = out/'findings.json'
    with fp.open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, priorReviewSource=OLD, priorReviewManifestSha256=PRIOR_SHA, currentRawFindings=1451,
                 inventoryFile='findings.json', inventorySha256=sha(fp), statusCounts=dict(Counter(r['status'] for r in result)),
                 reauthenticatedUnchangedDispositions=489, heldPriorDispositions=held, currentWholeJoinPending=True, historicalPtImportedAsCurrent=False,
                 executedPtAdded=0, ptAlternativeCompleted=0, sourceCodeChanged=False, analyzerReexecuted=False, F03Accepted=False, formalAccepted=False, vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reauthenticated=489, held=56, rawFindings=1451, statusCounts=value['statusCounts'], manifestSha256=sha(out/'manifest.json'), inventorySha256=sha(fp))))


if __name__ == '__main__':
    main()
