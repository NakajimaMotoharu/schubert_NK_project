"""Same-Main semantic reauthentication against original4073 XML; held11 stay unresolved."""
import copy
import json
import os
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from static_disposition_overlay import IDENTITY, load, validate_rationales
from pg6282_current4040_static_join import current_reference

SOURCE = 'f39de2986cbe0dc4a552f64d55ac723002cc77f6'
OLD = 'e45cfd31c8d610922f4e9432cc1cf11fa9b48338'
PRIOR = BASE/'PG6508-current4064-static-join-v1/manifest.json'
PRIOR_SHA = '8112d57745f186bd8a20aba8698af5dc4f7ce9418710fc07ceec16e0e3ca6150'


def read_qualified():
    qp = BASE/'PG6524-current4073-cases/qualification.json'; cp = qp.with_name('cases.json')
    op = W/'pg6524-finite-defaults-six-v1/manifest.safe.json'
    receipt = json.loads((W/'pg6526-original4073-artifacts-v1/manifest.safe.json').read_bytes())
    original = json.loads(op.read_bytes()); q = json.loads(qp.read_bytes())
    if not (receipt['actualExit'] == original['actualExit'] == q['actualExit'] == 0
            and receipt['source'] == original['source'] == q['productionSource'] == SOURCE
            and not receipt['wholeReplayed'] and q['returnedOriginalTerminalExact']
            and q['currentOriginalXmlQualified'] and q['FESFlakyNotRun'] == q['staticSixModules'] == 0
            and (q['tests'], q['suites'], q['mainClasses']) == (4073, 614, 1667)
            and receipt['originalManifestSha256'] == sha(op)
            and receipt['publicQualificationSha256'] == sha(qp)
            and receipt['publicCasesSha256'] == sha(cp)):
        raise ValueError('genuine original4073 terminal/receipt/XML, never begin or old success')
    return qp, q


def rebind(rows, cases, source):
    if any(r['source'] != source or r.get('result') != 'PASS_ORIGINAL_XML' for r in cases):
        raise ValueError('all references must come from current original whole')
    index = {(r['class'], r['caseNameSha256']): r for r in cases}
    if len(index) != len(cases):
        raise ValueError('one unique original semantic Test identity')
    result = []; joined = Counter()
    for old in rows:
        value = copy.deepcopy(old)
        if old['status'] == 'NOT_REVIEWED_CURRENT_SOURCE':
            result.append(value); continue
        refs = []
        for ref in old.get('currentWholeCaseRefs', []):
            key = (ref['class'], ref['caseNameSha256'])
            if key not in index:
                raise ValueError('every previous semantic case needs current actual XML')
            refs.append(current_reference(index[key]))
        context = old.get('staticContextPremiseOnly') is True
        if not refs and not context:
            raise ValueError('no inferred case binding or arbitrary empty-reference approval')
        value.update(priorReviewSource=OLD, priorReviewManifestSha256=PRIOR_SHA,
                     currentWholeCaseRefs=refs, currentWholeSource=source,
                     currentWholeJoinPending=False, historicalSuccessImported=False,
                     formalAccepted=False, F03Accepted=False, ptAlternativeCompleted=0)
        joined['staticContextOnly' if context else 'actualCurrentCaseRefs'] += 1
        result.append(value)
    return result, dict(joined)


def main():
    qp, q = read_qualified(); cp = qp.with_name('cases.json')
    cases = json.loads(cp.read_bytes())
    if len(cases) != 4073 or any(r['xmlSha256'] != q['modules'][r['module']]['xmlHashes'][r['sourceXml']] for r in cases):
        raise ValueError('all4073 actual case/XML hashes')
    sp = BASE/'PG6522-maintenance-owner-qualification-v1/manifest.json'
    if sha(sp) != 'f8944dbe60d775ee479169070d2e883a0a4d5aa8f05818f6f3dd51a254a97ae9':
        raise ValueError('immutable current15 static qualification')
    selected = json.loads(sp.read_bytes())
    pp = W/'pg6522-maintenance-owner-qualification-v1/manifest.safe.json'
    rp = pp.with_name('findings.safe.json')
    if sha(pp) != selected['privateManifestSha256'] or sha(rp) != selected['findingsSha256']:
        raise ValueError('original all-Main/raw static inputs')
    proof = json.loads(pp.read_bytes()); raw = json.loads(rp.read_bytes())
    before = BASE/'PG6490-current4064-cases/qualification.json'
    if sha(before) != 'c226dd9d40c491c44edf7a598aa9748ca90a58229b8849b8a6936cea136fb811':
        raise ValueError('immutable previous whole Main map')
    old = json.loads(before.read_bytes())
    if not (proof['source'] == SOURCE and proof['actualExit'] == 0 and proof['pmdRawFindings'] == 1361
            and proof['pmdProcessingErrors'] == proof['checkstyleFindings'] == proof['originalSixSpotBugs'] == 0
            and proof['allSourceHashes'] == q['allSourceHashes'] == old['allSourceHashes']
            and proof['allPhysicalMainSha256'] == q['allPhysicalMainSha256'] == old['allPhysicalMainSha256']
            and {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} == proof['allSourceHashes']):
        raise ValueError('all851/1667 original physical bytes exactly unchanged, not inferred equivalence')
    rows = load(PRIOR, PRIOR_SHA, OLD)
    if len(rows) != 1361 or len(raw) != 1361 or any(
            any(a[k] != b[k] for k in IDENTITY) for a, b in zip(rows, raw)):
        raise ValueError('all1361 raw diagnostic IDs/order/source/spans unchanged')
    joined, counts = rebind(rows, cases, SOURCE)
    validate_rationales(joined)
    if Counter(r['status'] for r in joined) != Counter(REQUIRED_CONTRACT=1054,
            CONTEXT_NOT_APPLICABLE=264, FALSE_POSITIVE=32, NOT_REVIEWED_CURRENT_SOURCE=11):
        raise ValueError('all prior dispositions preserved, held11 never promoted')
    for row in joined:
        if row['status'] != 'NOT_REVIEWED_CURRENT_SOURCE':
            row.update(currentWholeSha256=sha(qp), currentWholeCasesSha256=sha(cp))
    out = BASE/'PG6528-current4073-static-join-v1'; os.umask(0o077); out.mkdir()
    with (out/'findings.json').open('x') as f:
        json.dump(joined, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, rawFindings=1361, inventoryFile='findings.json',
        inventorySha256=sha(out/'findings.json'), statusCounts=dict(Counter(r['status'] for r in joined)),
        priorManifestPath=PRIOR.relative_to(ROOT).as_posix(), priorManifestSha256=PRIOR_SHA,
        currentWholeQualificationSha256=sha(qp), currentWholeCasesSha256=sha(cp),
        sameSourceOriginalWholeTests=4073, wholeRun='PG6524-six-v1', joined=counts,
        all851Main1667PhysicalUnchanged=True, unresolvedCaseBindings=[], heldUnreviewed=11,
        testsExecuted=0, additionalBuildsIssued=0, pmdRawRemoved=0, newAcceptedLeaves=0,
        formalAccepted=False, F03Accepted=False, ptAlternativeCompleted=0, effortPercent=None)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, joined=counts, heldUnreviewed=11, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
