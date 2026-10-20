"""Rebind573 exact unchanged reasons only; no old3973 PASS into current selected1021."""
import json
import os
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg5966_api_sql_selected import OLD
from pg5970_api_sql1021_public import SOURCE
from pg5910_storage_static_rebind import ordered_pairs
from pg5918_api_static_rebind import prior_disposition
from pg5758_static_rebind import bind_one
from static_disposition_overlay import load


def main():
    bp = BASE/'PG5950-current-static3973-v1/manifest.json'; bsha = '4603ed2df17049305c082ca233c9979702d898aa0fd76305ce4e0b1cba48675f'
    oldrows = load(bp, bsha, OLD); sp = BASE/'PG5968-api-sql-static-v1/manifest.json'; fp = sp.with_name('findings.json')
    if sha(sp) != 'f888e1a0817b7fc77521410df29c89c8fa95a7a3d5d4b3e17196d6be09e0d454' or sha(fp) != '046cdd80d79624fc3914ba0d5df4602b5e2c9c85a257aeda155fcd476e63ccc6':
        raise ValueError('actual current1430 unsuppressed raw diagnostics')
    proofs = []
    for name, public, source in (('pg5942-private-lock-static-v1', BASE/'PG5942-private-lock-static-v1/manifest.json', OLD), ('pg5968-api-sql-static-v1', sp, SOURCE)):
        p = W/name/'manifest.safe.json'; pub = json.loads(public.read_bytes())
        if sha(p) != pub['privateManifestSha256']:
            raise ValueError('actual immutable source/class map receipt')
        proof = json.loads(p.read_bytes())
        if proof['source'] != source or proof['actualExit'] != 0 or len(proof['allSourceHashes']) != 851 or len(proof['auxClassHashes']) != 1666:
            raise ValueError('one complete actual851/1666 map per source')
        proofs.append(proof)
    before, current = proofs
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != current['allSourceHashes']:
        raise ValueError('current851 Main unchanged')
    raw = json.loads(fp.read_bytes()); pairs = ordered_pairs(oldrows, raw)
    decided = {r['findingId']: r for r in oldrows if r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE'}; result = []; used = set()
    for row in raw:
        pair = pairs.get(row['findingId']); previous = decided.get(pair[0]['findingId']) if pair else None
        value, kind = bind_one(row, [prior_disposition(previous)] if previous else [], (ROOT/row['sourcePath']).read_bytes(), before['auxClassHashes'], current['auxClassHashes'])
        if kind == 'REBOUND':
            used.add(previous['findingId'])
            refs = [dict(klass=r['class'], **{'class':r['class']}, caseNameSha256=r['caseNameSha256']) for r in previous['currentWholeCaseRefs']]
            value.update(historicalCaseIds=[], plannedCurrentTestRefs=refs, currentWholeCaseRefs=[], currentWholeJoinPending=True,
                         priorReviewSource=OLD, priorReviewManifestSha256=bsha, currentPhysicalProofSha256=sha(W/'pg5968-api-sql-static-v1/manifest.safe.json'),
                         priorRawXmlOrdinal=previous['rawXmlOrdinal'], sourceFileOccurrenceRank=pair[1], diagnosticIdentityMapping='EXACT_ENTIRE_SOURCE_DIAGNOSTIC_SEQUENCE_WITHIN_FILE',
                         historicalPtImportedAsCurrent=False)
        result.append(value)
    held = sorted(set(decided)-used)
    if len(result) != 1430 or len(used) != 573 or held:
        raise ValueError('all573 must be exact unchanged sources/spans/allowner bytes; raw1430 retained')
    out = BASE/'PG5972-sql-static-dispositions-v1'; os.umask(0o077); out.mkdir(); fp = out/'findings.json'
    with fp.open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, priorReviewSource=OLD, priorReviewManifestSha256=bsha, currentRawFindings=1430,
                 inventoryFile='findings.json', inventorySha256=sha(fp), statusCounts=dict(Counter(r['status'] for r in result)),
                 reauthenticatedUnchangedDispositions=573, heldPriorDispositions=[], currentWholeJoinPending=True,
                 historicalPtImportedAsCurrent=False, executedPtAdded=0, ptAlternativeCompleted=0, sourceCodeChanged=False,
                 analyzerReexecuted=False, F03Accepted=False, formalAccepted=False, vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reauthenticated=573, held=0, raw=1430, unreviewed=857, manifestSha256=sha(out/'manifest.json'), inventorySha256=sha(fp))))


if __name__ == '__main__':
    main()
