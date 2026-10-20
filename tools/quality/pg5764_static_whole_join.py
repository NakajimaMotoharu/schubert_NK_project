"""Join exact source-bound dispositions to actual same-source3932 XML, not historical PASS."""
import copy
import json
import os
from collections import Counter,defaultdict
from pg5756_private_contract_qualification import SOURCE,ROOT,BASE
from pg5540_snapshot_scratch_selected import sha

OUT=BASE/'PG5764-current-static-whole-v1'


def current_reference(historical,current_index):
    rows=current_index[(historical['class'],historical['caseNameSha256'])]
    if len(rows)!=1 or rows[0]['result']!='PASS_ORIGINAL_XML':raise ValueError('one genuine current successful semantic case required')
    current=rows[0]
    return {'testId':current['testId'],'xmlSha256':current['xmlSha256'],'class':current['class'],'caseNameSha256':current['caseNameSha256']}


def main():
    sp=BASE/'PG5760-changed-context-v1/manifest.json'
    if sha(sp)!='12669fc9fb3f225310894b08c430f38c07dd6ffd9f76a029c0a752cd967f6737':raise ValueError('exact384 reviewed/current source bindings')
    prior=json.loads(sp.read_bytes());raw=sp.with_name('findings.json')
    if sha(raw)!='d993f89240539ebcd1116000a1115ad3bb8a6ee63c360c58ac3658702fd5775e':raise ValueError('all1582 raw diagnostic identities')
    rows=json.loads(raw.read_bytes());qp=BASE/'PG5754-current3932-cases/qualification.json';cp=qp.with_name('cases.json')
    if sha(qp)!='ac4d3ccf6e9be8c1222aec8d09dd17508975f6475b3380faced765ce4c836b18'or sha(cp)!='f0e533df0ecea383f5e7cf0639d27f98c36691de11f644278df00ec0438a7276':raise ValueError('actual original3932 qualification/cases')
    q=json.loads(qp.read_bytes());cases=json.loads(cp.read_bytes())
    if prior['source']!=q['productionSource']or q['productionSource']!=SOURCE or(q['tests'],q['suites'],q['mainClasses'])!=(3932,581,1664)or q['FESFlakyNotRun']!=0:raise ValueError('same-source actual whole only')
    original=json.loads((BASE/'PG5588-current3905-cases/cases.json').read_bytes());historical={r['testId']:r for r in original};index=defaultdict(list)
    for row in cases:index[(row['class'],row['caseNameSha256'])].append(row)
    joined=0;static_only=0;newrows=[];current_refs=set()
    for row in rows:
        if row['status']!='SOURCE_REBOUND_CURRENT_WHOLE_PENDING':newrows.append(row);continue
        if sha(ROOT/row['sourcePath'])!=row['sourceSha256']:raise ValueError('current source diagnostic binding unchanged')
        refs=[current_reference(historical[k],index)for k in row.get('historicalCaseIds',[])]
        if not refs and row.get('historicalTestRefs'):
            if row['sourcePath']!='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestLogProducer.java'or row['historicalTestRefs']!=['PT-F03-LOG001','PT-F03-LOG002','PT-F03-LOG003','PT-F03-LOG004']:raise ValueError('exact explicit four sink contract references')
            refs=[current_reference(r,index)for r in cases if r['class']=='dev.codex.schubert.nk.web.logging.WebAuditSinkContractTest']
            if len(refs)!=4:raise ValueError('all actual four current audit cases')
        if row.get('newDispositionCreated'):
            if row['rule']!='UseProperClassLoader':raise ValueError('only declared new loader applicability')
            refs=[current_reference(r,index)for r in cases if r['class']=='dev.codex.schubert.nk.web.bootstrap.WebHttpServerTest']
            if len(refs)!=11:raise ValueError('all original current server fixture cases')
        if not refs:
            if row['priorDisposition']!='CONTEXT_NOT_APPLICABLE'or row['rule']!='DoNotUseThreads':raise ValueError('required-contract/false-positive requires current XML evidence')
            static_only+=1
        result=copy.deepcopy(row);result.update(status=row['priorDisposition'],currentWholeCaseRefs=refs,currentWholeJoinPending=False,currentQualificationSha256=sha(qp),currentCasesSha256=sha(cp),reviewSource=SOURCE,wholeJoinedWithoutPtReplay=True,historicalPtImportedAsCurrent=False,staticContextPremiseOnly=not refs)
        newrows.append(result);joined+=1;current_refs.update(r['testId']for r in refs)
    if joined!=384 or static_only!=239 or len(newrows)!=1582:raise ValueError('exact384 reviewed/239 static-premise-only, all diagnostics retained')
    value={'actualExit':0,'source':SOURCE,'priorManifestSha256':sha(sp),'priorFindingsSha256':sha(raw),'currentWholeQualificationSha256':sha(qp),'currentWholeCasesSha256':sha(cp),'currentWholeTests':3932,'currentRawFindings':1582,'sourceAndWholeJoinedDispositions':joined,'staticContextPremiseOnly':static_only,'uniqueCurrentCaseReferences':len(current_refs),'statusCounts':dict(Counter(r['status']for r in newrows)),'newDispositionsCreated':0,'executedPtAdded':0,'ptAlternativeCompleted':0,'historicalPtImportedAsCurrent':False,'sourceCodeChanged':False,'analyzerReexecuted':False,'rawWarningsRemoved':0,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    os.umask(0o077);OUT.mkdir()
    for name,data in(('manifest.json',value),('findings.json',newrows)):
        with(OUT/name).open('x')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value))
    print(json.dumps({'manifestSha256':sha(OUT/'manifest.json'),'findingsSha256':sha(OUT/'findings.json')}))


if __name__=='__main__':main()
