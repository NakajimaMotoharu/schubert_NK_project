"""After original3939 qualification, join476 source-bound reasons to current physical XML."""
import copy
import hashlib
import json
import os
from collections import Counter,defaultdict
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5780_jms_primary_whole import SOURCE,W
from static_disposition_overlay import BASE,load
from pg5764_static_whole_join import current_reference

OUT=BASE/'PG5792-current-static-whole-v1'
QUALIFIED_PUBLIC_SHA=None
CURRENT_CASES_SHA=None


def qualified_whole():
    if QUALIFIED_PUBLIC_SHA is None or CURRENT_CASES_SHA is None:raise ValueError('await actual original3939 public qualification/cases hashes; no guessed acceptance')
    qp=BASE/'PG5780-current3939-cases/qualification.json';cp=qp.with_name('cases.json')
    if sha(qp)!=QUALIFIED_PUBLIC_SHA or sha(cp)!=CURRENT_CASES_SHA:raise ValueError('exact actual current3939 qualification/case artifacts')
    private=W/'pg5782-jms-primary-qualified-v1/manifest.safe.json';qraw=private.read_bytes();receipt=json.loads(qraw);q=json.loads(qp.read_bytes());cases=json.loads(cp.read_bytes())
    if q['qualificationReceiptSha256']!=hashlib.sha256(qraw).hexdigest()or receipt['actualExit']!=0 or q['projectionActualExit']!=0 or q['productionSource']!=SOURCE or(q['tests'],q['suites'],q['mainClasses'])!=(3939,583,1664)or q['FESFlakyNotRun']!=q['staticSixModules']or q['staticSixModules']!=0:raise ValueError('original independently qualified3939 and actual projection first')
    if q['casesSha256']!=CURRENT_CASES_SHA or any(q[k]!=v for k,v in receipt['result'].items()):raise ValueError('public projection preserves entire original independent result')
    original=W/'pg5780-jms-primary-six-v1/manifest.safe.json'
    if receipt['originalReturnedManifestSha256']!=sha(original)or json.loads(original.read_bytes())['actualExit']!=0:raise ValueError('same actual original terminal, never arithmetic success')
    if len(cases)!=3939 or len({c['testId']for c in cases})!=3939 or any(c['result']!='PASS_ORIGINAL_XML'or c['xmlSha256']!=q['modules'][c['module']]['xmlHashes'][c['sourceXml']]for c in cases):raise ValueError('all actual3939 case references from exact qualified XML')
    return qp,cp,q,cases


def main():
    qp,cp,q,cases=qualified_whole()
    bp=BASE/'PG5788-jms-guard4-v1/manifest.json';bsha='bac472e8d9f65dc58725a5ee4d952192dda0a95cb8d910877468ce2547a89ae7';rows=load(bp,bsha,SOURCE)
    oldq=BASE/'PG5754-current3932-cases/qualification.json';oldcp=oldq.with_name('cases.json')
    if sha(oldq)!='ac4d3ccf6e9be8c1222aec8d09dd17508975f6475b3380faced765ce4c836b18'or sha(oldcp)!='f0e533df0ecea383f5e7cf0639d27f98c36691de11f644278df00ec0438a7276':raise ValueError('historical3932 identity, not old pass import')
    historical={c['testId']:c for c in json.loads(oldcp.read_bytes())};oldrows=load(BASE/'PG5772-primary-capture27-v1/manifest.json','b22a70787187534deadba238364e708c3fd749ceb456392795b5e11a81cff487','9463db1ac23437043facf95b87f64b9fc7e758bd');oldindex={r['findingId']:r for r in oldrows}
    gp=BASE/'PG5778-jms-primary14/manifest.json'
    if sha(gp)!='9be091b5b0293ce1c04998890decbe36a09912b875d980deea1ab257708ba5aa':raise ValueError('original selected contract case identity source')
    selected={c['testId']:c for c in json.loads(gp.read_bytes())['actualTestCases']};index=defaultdict(list)
    for case in cases:index[(case['class'],case['caseNameSha256'])].append(case)
    current=[];joined=0;static_only=0;references=set()
    for row in rows:
        if row['status']!='SOURCE_REBOUND_CURRENT_WHOLE_PENDING':current.append(row);continue
        if sha(ROOT/row['sourcePath'])!=row['sourceSha256']:raise ValueError('current source diagnostic binding unchanged')
        refs=[current_reference(historical[ident],index)for ident in row.get('historicalCaseIds',[])]
        if row.get('recheckedMovedPrior'):
            if refs:raise ValueError('one source of current references per moved scope')
            refs=[current_reference(historical[r['testId']],index)for r in oldindex[row['priorFindingId']]['currentWholeCaseRefs']]
        if row.get('selectedContractCases'):
            if refs:raise ValueError('new guard references are current selected semantic identities only')
            refs=[current_reference(selected[r['actualTestId']],index)for r in row['selectedContractCases']]
        if not refs:
            if row['priorDisposition']!='CONTEXT_NOT_APPLICABLE'or row['rule']!='DoNotUseThreads':raise ValueError('required contract needs actual current XML refs')
            static_only+=1
        value=copy.deepcopy(row);value.update(status=row['priorDisposition'],currentWholeCaseRefs=refs,currentWholeJoinPending=False,currentQualificationSha256=sha(qp),currentCasesSha256=sha(cp),reviewSource=SOURCE,historicalPtImportedAsCurrent=False,staticContextPremiseOnly=not refs)
        current.append(value);joined+=1;references.update(r['testId']for r in refs)
    if joined!=476 or static_only!=239 or len(current)!=1585:raise ValueError('exact476 individual reasons, all raw1585, context-only239')
    os.umask(0o077);OUT.mkdir();fp=OUT/'findings.json'
    with fp.open('x')as f:json.dump(current,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value={'actualExit':0,'source':SOURCE,'priorPendingManifestSha256':bsha,'currentWholeQualificationSha256':sha(qp),'currentWholeCasesSha256':sha(cp),'currentWholeTests':3939,'currentRawFindings':1585,'sourceAndWholeJoinedDispositions':joined,'staticContextPremiseOnly':static_only,'uniqueCurrentCaseReferences':len(references),'statusCounts':dict(Counter(r['status']for r in current)),'inventoryFile':'findings.json','inventorySha256':sha(fp),'newDispositionsCreated':0,'executedPtAdded':0,'ptAlternativeCompleted':0,'historicalPtImportedAsCurrent':False,'sourceCodeChanged':False,'analyzerReexecuted':False,'rawWarningsRemoved':0,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    with(OUT/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value));print(json.dumps({'manifestSha256':sha(OUT/'manifest.json'),'findingsSha256':sha(fp)}))


if __name__=='__main__':main()
