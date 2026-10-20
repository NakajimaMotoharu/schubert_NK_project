"""Join500 reasons to original3971 actual XML only; no PT/analyzer/runtime invocation."""
import copy
import hashlib
import json
import os
from collections import Counter,defaultdict
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5860_terminal_whole import SOURCE,W
from static_disposition_overlay import BASE,load
from pg5846_static3967_join import current_reference as prior_reference
from pg5874_storage_resource18_review import USE


def current_reference(reference,index):
    if 'method'not in reference or not reference.get('class','').startswith('dev.codex.schubert.nk.storage.'):
        return prior_reference(reference,index)
    cls=reference['class'];method=reference['method']
    if cls=='dev.codex.schubert.nk.storage.ResourceScopeTest':allowed=method in USE
    elif cls=='dev.codex.schubert.nk.storage.FactoryResourceScopeTest':allowed=any(method.startswith('factory'+str(i).zfill(3))for i in range(1,19))
    else:allowed=False
    if not allowed or 'caseNameSha256'in reference:raise ValueError('only declared storage resource method provenance')
    found=[r for name in(method,method+'()')for r in index.get((cls,hashlib.sha256(name.encode()).hexdigest()),[])]
    if len(found)!=1 or found[0]['result']!='PASS_ORIGINAL_XML':raise ValueError('one current genuine XML, not a planned or historical PASS')
    return{k:found[0][k]for k in('testId','xmlSha256','class','caseNameSha256')}


def qualified_whole():
    qp=BASE/'PG5860-current3971-cases/qualification.json';cp=qp.with_name('cases.json');q=json.loads(qp.read_bytes());cases=json.loads(cp.read_bytes());rp=W/'pg5862-terminal-qualified-v1/manifest.safe.json';r=json.loads(rp.read_bytes());op=W/'pg5860-terminal-six-v1/manifest.safe.json';original=json.loads(op.read_bytes());sp=W/'pg5858-terminal-static-v1/manifest.safe.json';static=json.loads(sp.read_bytes())
    if not(q['productionSource']==r['source']==original['source']==static['source']==SOURCE and q['projectionActualExit']==r['actualExit']==original['actualExit']==0 and q['qualificationReceiptSha256']==sha(rp)and r['originalReturnedManifestSha256']==sha(op)and q['casesSha256']==sha(cp)and q['serverManifestSha256']==r['result']['serverManifestSha256']and q['allPhysicalMainSha256']==r['result']['allPhysicalMainSha256']==static['auxClassHashes']and(q['tests'],q['suites'],q['mainClasses'])==(3971,592,1666)and q['FESFlakyNotRun']==q['staticSixModules']==0 and q['wholeReplayed']is False):raise ValueError('genuine original3971 terminal/source/physical/qualified XML correspondence')
    if any(q[k]!=v for k,v in r['result'].items()):raise ValueError('projection preserves entire original qualification')
    if len(cases)!=3971 or len({c['testId']for c in cases})!=3971 or any(c['result']!='PASS_ORIGINAL_XML'or c['xmlSha256']!=q['modules'][c['module']]['xmlHashes'][c['sourceXml']]for c in cases):raise ValueError('all3971 exact current XML references')
    return qp,cp,q,cases


def main():
    qp,cp,_q,cases=qualified_whole();bp=BASE/'PG5874-storage-resource18-v1/manifest.json';bsha='cf5b78c76561861ef2a4a034ce88924312f7ffb10c4c72089f83af8f22607e3d';rows=load(bp,bsha,SOURCE)
    oldq=BASE/'PG5832-current3967-cases/qualification.json';oldcp=oldq.with_name('cases.json')
    if sha(oldq)!='fcceece52ccd16cf81f0b0e67060464ce0414a723417d2f827b8e29a9bcd9023'or sha(oldcp)!='fc8d6037da80e10e1af2978e9e1b2b150220158b035c5063341ea86ee3af902d':raise ValueError('historical3967 identities only, no PASS import')
    historical={c['testId']:c for c in json.loads(oldcp.read_bytes())};index=defaultdict(list)
    for c in cases:index[(c['class'],c['caseNameSha256'])].append(c)
    result=[];joined=static_only=0;refs_unique=set()
    for row in rows:
        if row['status']!='SOURCE_REBOUND_CURRENT_WHOLE_PENDING':result.append(row);continue
        if sha(ROOT/row['sourcePath'])!=row['sourceSha256']:raise ValueError('entire current source unchanged')
        sources=[historical[i]for i in row.get('historicalCaseIds',[])]
        for key in('historicalWholeCaseRefs','currentSelectedCaseRefs','plannedCurrentTestRefs'):
            if not row.get(key):continue
            if sources:raise ValueError('one provenance for each current case reference')
            sources=[historical[r['testId']]for r in row[key]]if key=='historicalWholeCaseRefs'else row[key]
        refs=[current_reference(r,index)for r in sources]
        if not refs:
            if row['priorDisposition']!='CONTEXT_NOT_APPLICABLE'or row['rule']!='DoNotUseThreads':raise ValueError('required contract must have actual current original XML')
            static_only+=1
        value=copy.deepcopy(row);value.update(status=row['priorDisposition'],currentWholeCaseRefs=refs,currentWholeJoinPending=False,currentQualificationSha256=sha(qp),currentCasesSha256=sha(cp),reviewSource=SOURCE,historicalPtImportedAsCurrent=False,staticContextPremiseOnly=not refs)
        result.append(value);joined+=1;refs_unique.update(r['testId']for r in refs)
    if joined!=500 or static_only!=239 or len(result)!=1586:raise ValueError('all500 reasons and all1586 raw rows preserved;239 static-only premises')
    out=BASE/'PG5876-current-static3971-v1';os.umask(0o077);out.mkdir();fp=out/'findings.json'
    with fp.open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value={'actualExit':0,'source':SOURCE,'priorPendingManifestSha256':bsha,'currentWholeQualificationSha256':sha(qp),'currentWholeCasesSha256':sha(cp),'currentWholeTests':3971,'currentRawFindings':1586,'sourceAndWholeJoinedDispositions':joined,'staticContextPremiseOnly':static_only,'uniqueCurrentCaseReferences':len(refs_unique),'statusCounts':dict(Counter(r['status']for r in result)),'inventoryFile':'findings.json','inventorySha256':sha(fp),'executedPtAdded':0,'ptAlternativeCompleted':0,'historicalPtImportedAsCurrent':False,'sourceCodeChanged':False,'analyzerReexecuted':False,'rawWarningsRemoved':0,'wholePassIsNotSpecificationAcceptance':True,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value));print(json.dumps({'manifestSha256':sha(out/'manifest.json'),'findingsSha256':sha(fp)}))


if __name__=='__main__':main()
