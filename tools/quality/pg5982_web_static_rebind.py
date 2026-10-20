"""Reauthenticate573 unchanged reason scopes, retaining semantic refs but not prior PASS."""
import json
import os
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg5976_web_form_selected import OLD
from pg5980_web921_public import SOURCE, STATIC_SHA
from pg5910_storage_static_rebind import ordered_pairs
from pg5918_api_static_rebind import prior_disposition
from pg5758_static_rebind import bind_one
from static_disposition_overlay import load


def references(previous):
    refs = previous.get('plannedCurrentTestRefs')
    if type(refs) is not list or (not refs and previous.get('priorDisposition') != 'CONTEXT_NOT_APPLICABLE') or previous.get('currentWholeCaseRefs') or any(set(r)-{'klass','class','caseNameSha256','currentTestSourceSha256'} or not r.get('class') or len(r.get('caseNameSha256','')) != 64 for r in refs):
        raise ValueError('pending semantic Test references only, no actual whole result aliases')
    return refs


def main():
    bp = BASE/'PG5972-sql-static-dispositions-v1/manifest.json'; bsha = 'dac135f64f921f7b4391414eb5d76434f38fdb7c49ff3a78133ba132d70fd2c9'
    oldrows = load(bp, bsha, OLD); sp = BASE/'PG5978-web-form-static-v1/manifest.json'; fp = sp.with_name('findings.json')
    if sha(sp) != STATIC_SHA:
        raise ValueError('actual current all851/1666/unsuppressed1408 raw first')
    proofs = []
    for name, public, source in (('pg5968-api-sql-static-v1', BASE/'PG5968-api-sql-static-v1/manifest.json', OLD), ('pg5978-web-form-static-v1', sp, SOURCE)):
        p = W/name/'manifest.safe.json'; pub = json.loads(public.read_bytes())
        if sha(p) != pub['privateManifestSha256']:
            raise ValueError('actual source/owner physical proof hash fixed')
        proof = json.loads(p.read_bytes())
        if proof['source'] != source or proof['actualExit'] != 0 or len(proof['allSourceHashes']) != 851 or len(proof['auxClassHashes']) != 1666:
            raise ValueError('all851/1666 actual old/current source maps')
        proofs.append(proof)
    before, current = proofs
    if {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != current['allSourceHashes']:
        raise ValueError('all current Main unchanged')
    raw = json.loads(fp.read_bytes()); pairs = ordered_pairs(oldrows, raw)
    decided = {r['findingId']:r for r in oldrows if r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE'}; used = set(); result = []
    for row in raw:
        pair = pairs.get(row['findingId']); previous = decided.get(pair[0]['findingId']) if pair else None
        value, kind = bind_one(row, [prior_disposition(previous)] if previous else [], (ROOT/row['sourcePath']).read_bytes(), before['auxClassHashes'], current['auxClassHashes'])
        if kind == 'REBOUND':
            used.add(previous['findingId'])
            value.update(historicalCaseIds=[], plannedCurrentTestRefs=references(previous), currentWholeCaseRefs=[], currentWholeJoinPending=True,
                         priorReviewSource=OLD, priorReviewManifestSha256=bsha, currentPhysicalProofSha256=sha(W/'pg5978-web-form-static-v1/manifest.safe.json'),
                         priorRawXmlOrdinal=previous['rawXmlOrdinal'], sourceFileOccurrenceRank=pair[1], diagnosticIdentityMapping='EXACT_ENTIRE_SOURCE_DIAGNOSTIC_SEQUENCE_WITHIN_FILE', historicalPtImportedAsCurrent=False)
        result.append(value)
    if len(result) != 1408 or len(used) != 573 or set(decided)-used:
        raise ValueError('all573 exact source/span/owner bytes, no changed reason or dropped raw')
    out = BASE/'PG5982-web-static-dispositions-v1'; os.umask(0o077); out.mkdir(); target = out/'findings.json'
    with target.open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, priorReviewSource=OLD, priorReviewManifestSha256=bsha, currentRawFindings=1408,
                 inventoryFile='findings.json', inventorySha256=sha(target), statusCounts=dict(Counter(r['status'] for r in result)),
                 reauthenticatedUnchangedDispositions=573, heldPriorDispositions=[], currentWholeJoinPending=True,
                 historicalPtImportedAsCurrent=False, executedPtAdded=0, ptAlternativeCompleted=0, sourceCodeChanged=False,
                 analyzerReexecuted=False, F03Accepted=False, formalAccepted=False, vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reauthenticated=573, held=0, raw=1408, unreviewed=835, manifestSha256=sha(out/'manifest.json'), inventorySha256=sha(target))))


if __name__ == '__main__':
    main()
