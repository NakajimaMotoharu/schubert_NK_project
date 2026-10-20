"""Join current528 reasons to genuine original3973 XML; never execute PT or runtime."""
import copy
import json
import os
from collections import Counter, defaultdict
from pg5540_snapshot_scratch_selected import ROOT, sha
from pg5886_terminal_serial_whole import SOURCE, W
from static_disposition_overlay import BASE, load
from pg5876_static3971_join import current_reference

PENDING = BASE / 'PG5898-serial-identity5-v1/manifest.json'
PENDING_SHA = 'fffcd1ec6687bc9036a21efd90096fe62c9cf89325d9afabc1681a938048d0eb'


def qualified_whole():
    qp = BASE / 'PG5886-current3973-cases/qualification.json'
    cp = qp.with_name('cases.json')
    q, cases = json.loads(qp.read_bytes()), json.loads(cp.read_bytes())
    rp = W / 'pg5888-terminal-serial-qualified-v1/manifest.safe.json'
    op = W / 'pg5886-terminal-serial-six-v1/manifest.safe.json'
    sp = W / 'pg5882-terminal-serial-static-v1/manifest.safe.json'
    r, original, static = (json.loads(p.read_bytes()) for p in (rp, op, sp))
    if not (q['productionSource'] == r['source'] == original['source'] == static['source'] == SOURCE
            and q['projectionActualExit'] == r['actualExit'] == original['actualExit'] == 0
            and q['qualificationReceiptSha256'] == sha(rp)
            and r['originalReturnedManifestSha256'] == sha(op)
            and q['casesSha256'] == sha(cp)
            and q['serverManifestSha256'] == r['result']['serverManifestSha256']
            and q['allPhysicalMainSha256'] == r['result']['allPhysicalMainSha256'] == static['auxClassHashes']
            and (q['tests'], q['suites'], q['mainClasses']) == (3973, 592, 1666)
            and q['FESFlakyNotRun'] == q['staticSixModules'] == 0
            and q['wholeReplayed'] is False):
        raise ValueError('genuine current3973 terminal/source/physical/qualified XML correspondence')
    if any(q[k] != v for k, v in r['result'].items()):
        raise ValueError('projection preserves entire independent qualification')
    if len(cases) != 3973 or len({c['testId'] for c in cases}) != 3973 or any(
            c['result'] != 'PASS_ORIGINAL_XML'
            or c['xmlSha256'] != q['modules'][c['module']]['xmlHashes'][c['sourceXml']] for c in cases):
        raise ValueError('all3973 exact current original XML references')
    return qp, cp, q, cases


def main():
    qp, cp, _q, cases = qualified_whole()
    rows = load(PENDING, PENDING_SHA, SOURCE)
    oldq = BASE / 'PG5860-current3971-cases/qualification.json'
    oldcp = oldq.with_name('cases.json')
    if sha(oldq) != 'a937e6dc41450d13b2874299d28f19caafc5b0b070fffdd4c96669bc410c3d02' or sha(oldcp) != '5d0257d6003598f9d2d1cc98032f299012511cdf9b5f6eca1832ac1bee11667b':
        raise ValueError('historical3971 identities only, never PASS import')
    historical = {c['testId']: c for c in json.loads(oldcp.read_bytes())}
    index = defaultdict(list)
    for c in cases:
        index[c['class'], c['caseNameSha256']].append(c)
    result, unique = [], set()
    joined = static_only = 0
    for row in rows:
        if row['status'] != 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING':
            result.append(row)
            continue
        if sha(ROOT / row['sourcePath']) != row['sourceSha256']:
            raise ValueError('entire current source unchanged')
        sources = [historical[i] for i in row.get('historicalCaseIds', [])]
        for key in ('historicalWholeCaseRefs', 'currentSelectedCaseRefs', 'plannedCurrentTestRefs'):
            if not row.get(key):
                continue
            if sources:
                raise ValueError('one provenance per current reference')
            sources = [historical[r['testId']] for r in row[key]] if key == 'historicalWholeCaseRefs' else row[key]
        refs = [current_reference(r, index) for r in sources]
        if not refs:
            if row['priorDisposition'] != 'CONTEXT_NOT_APPLICABLE' or row['rule'] != 'DoNotUseThreads':
                raise ValueError('required contract needs actual current original XML')
            static_only += 1
        value = copy.deepcopy(row)
        value.update(status=row['priorDisposition'], currentWholeCaseRefs=refs, currentWholeJoinPending=False,
                     currentQualificationSha256=sha(qp), currentCasesSha256=sha(cp), reviewSource=SOURCE,
                     historicalPtImportedAsCurrent=False, staticContextPremiseOnly=not refs)
        result.append(value)
        joined += 1
        unique.update(r['testId'] for r in refs)
    if (joined, static_only, len(result)) != (528, 239, 1586):
        raise ValueError('all528 reasons/all1586 warnings preserved,239 static-context-only premises')
    out = BASE / 'PG5902-current-static3973-v1'
    os.umask(0o077)
    out.mkdir()
    fp = out / 'findings.json'
    with fp.open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, priorPendingManifestSha256=PENDING_SHA,
                 currentWholeQualificationSha256=sha(qp), currentWholeCasesSha256=sha(cp), currentWholeTests=3973,
                 currentRawFindings=1586, sourceAndWholeJoinedDispositions=joined, staticContextPremiseOnly=static_only,
                 uniqueCurrentCaseReferences=len(unique), statusCounts=dict(Counter(r['status'] for r in result)),
                 inventoryFile='findings.json', inventorySha256=sha(fp), executedPtAdded=0, ptAlternativeCompleted=0,
                 historicalPtImportedAsCurrent=False, sourceCodeChanged=False, analyzerReexecuted=False,
                 rawWarningsRemoved=0, wholePassIsNotSpecificationAcceptance=True, F03Accepted=False,
                 formalAccepted=False, vmActions=0)
    with (out / 'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(value))
    print(json.dumps(dict(manifestSha256=sha(out / 'manifest.json'), findingsSha256=sha(fp))))


if __name__ == '__main__':
    main()
