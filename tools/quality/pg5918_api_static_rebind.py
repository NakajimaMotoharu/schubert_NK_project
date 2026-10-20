"""Rebind unchanged reasons using real prior/current compile maps, never historical PT PASS."""
import copy
import json
import os
from collections import Counter
from pg5540_snapshot_scratch_selected import ROOT, sha
from static_disposition_overlay import BASE, load
from pg5910_storage_static_rebind import ordered_pairs
from pg5758_static_rebind import bind_one, rationale_text

SOURCE = '682a4b99eb0b95bcd4f1cd276fea75b5f2e62e3b'
OLD = '7a664ce0a99860bb75e1e1a3ae30354a9840528a'
W = ROOT.parent / 'pgpt-runs/PG379'


def prior_disposition(row):
    value = copy.deepcopy(row)
    if value['status'] == 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING':
        value['status'] = value['priorDisposition']
    reason = rationale_text(value)
    if reason is None:
        raise ValueError('individual rationale required before restoring prior disposition')
    value['reason'] = value['priorReason'] = reason
    return value


def main():
    bp = BASE / 'PG5910-storage-dispositions-v2/manifest.json'
    bsha = '283a03308fdba584cd49cc6f3fdb245eef9292dd2bbbf5caefffa8f30a825366'
    oldrows = load(bp, bsha, OLD)
    oldsp = BASE / 'PG5906-storage30-static-v1/manifest.json'
    sp = BASE / 'PG5914-api-expression-static-v1/manifest.json'
    fp = sp.with_name('findings.json')
    if sha(oldsp) != 'a0c4d80e21a1a20a05928d26a35168be6802aa01e2bc8a682bb6e49959ca5365' or sha(sp) != '318d3783a5bfa4fe9a3920b252d3449eca01b9131c925758eadf13f8289548b4' or sha(fp) != '03e92090ea7306bafde2e3319bf03438d9beef16b39ddb806c96a39e43c38a0e':
        raise ValueError('immutable original and current static receipts/raw diagnostics')
    privates = [W / name / 'manifest.safe.json' for name in ('pg5906-storage30-static-v1', 'pg5914-api-expression-static-v1')]
    proofs = []
    for path, pub, source in zip(privates, (oldsp, sp), (OLD, SOURCE)):
        if sha(path) != json.loads(pub.read_bytes())['privateManifestSha256']:
            raise ValueError('actual source/compile map receipt')
        proof = json.loads(path.read_bytes())
        if proof['actualExit'] != 0 or proof['source'] != source or len(proof['allSourceHashes']) != 851 or len(proof['auxClassHashes']) != 1666:
            raise ValueError('genuine complete Main source/class maps, no old whole required or inferred')
        proofs.append(proof)
    oldproof, current = proofs
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != current['allSourceHashes']:
        raise ValueError('all current851 Main unchanged')
    raw = json.loads(fp.read_bytes())
    pairs = ordered_pairs(oldrows, raw)
    decided = {r['findingId']: prior_disposition(r) for r in oldrows if r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE'}
    result, used = [], set()
    for row in raw:
        pair = pairs.get(row['findingId'])
        previous = decided.get(pair[0]['findingId']) if pair else None
        value, kind = bind_one(row, [previous] if previous else [], (ROOT / row['sourcePath']).read_bytes(), oldproof['auxClassHashes'], current['auxClassHashes'])
        if kind == 'REBOUND':
            used.add(previous['findingId'])
            refs = previous.get('currentWholeCaseRefs') or previous.get('wholeCaseRefs') or []
            historical = previous.get('historicalCaseIds') or [r['testId'] for r in refs]
            value.update(priorReviewSource=OLD, priorReviewManifestSha256=bsha,
                         currentPhysicalProofSha256=sha(privates[1]), priorPhysicalProofSha256=sha(privates[0]),
                         historicalCaseIds=historical, currentWholeCaseRefs=[], currentWholeJoinPending=True,
                         historicalPtImportedAsCurrent=False, priorRawXmlOrdinal=previous['rawXmlOrdinal'],
                         sourceFileOccurrenceRank=pair[1], diagnosticIdentityMapping='EXACT_ENTIRE_SOURCE_DIAGNOSTIC_SEQUENCE_WITHIN_FILE')
        result.append(value)
    held = [dict(findingId=k, sourcePath=decided[k]['sourcePath'], rule=decided[k]['rule'], reason='SOURCE/DIAGNOSTIC/OWNER_CHANGED; explicit re-review required') for k in sorted(set(decided) - used)]
    if len(result) != 1544 or len(used) != 527 or len(held) != 1 or not held[0]['sourcePath'].endswith('/AssetChecksumManifest.java') or held[0]['rule'] != 'UseConcurrentHashMap':
        raise ValueError('exact527 unchanged reasons; changed Asset map one held, all1544 preserved')
    out = BASE / 'PG5918-api-dispositions-v1'
    os.umask(0o077); out.mkdir()
    inventory = out / 'findings.json'
    with inventory.open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, priorReviewSource=OLD, priorReviewManifestSha256=bsha,
                 currentStaticManifestSha256=sha(sp), currentFindingsSha256=sha(fp), currentActualSourceByteProofSha256=sha(privates[1]),
                 priorActualSourceByteProofSha256=sha(privates[0]), currentRawFindings=1544, reauthenticatedUnchangedDispositions=len(used),
                 heldPriorDispositions=held, statusCounts=dict(Counter(r['status'] for r in result)), inventoryFile='findings.json',
                 inventorySha256=sha(inventory), newDispositionsCreated=0, currentWholeJoinPending=True, historicalPtImportedAsCurrent=False,
                 executedPtAdded=0, ptAlternativeCompleted=0, sourceCodeChanged=False, analyzerReexecuted=False,
                 rawWarningsRemoved=0, F03Accepted=False, formalAccepted=False, vmActions=0)
    with (out / 'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(value)); print(json.dumps(dict(manifestSha256=sha(out / 'manifest.json'), findingsSha256=sha(inventory))))


if __name__ == '__main__':
    main()
