"""Authenticate actual4040 method refs, retaining all raw1350 and unresolved bindings."""
import copy
import hashlib
import json
import os
import subprocess
import re
from collections import Counter
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6276_current4040_trace import SOURCE,read_qualified
from pg6278_current4040_static_plan import PRIOR,PRIOR_SHA,OLD
from pg6092_current3985_static_join import source_case_candidates
from static_disposition_overlay import load,validate_rationales

INPUT=BASE/'PG6292-standalone-thread-context-v1/manifest.json'
INPUT_SHA='d5d9ce807a77220b7ff1517a95fabe62683acf82a1398ab30d7e97efceafcba7'


def current_reference(row):return {k:row[k]for k in ('testId','xmlSha256','class','caseNameSha256','source')}


def declared_class_references(declarations,cases,source,read_source):
    result=[];seen=set()
    for declaration in declarations:
        cls=declaration['className']
        match=re.fullmatch(r'dev\.codex\.schubert\.nk\.(web|batch|api|bootstrap|storage|protocol)\.(?:[A-Za-z_$][A-Za-z0-9_$]*\.)*[A-Za-z_$][A-Za-z0-9_$]*',cls)
        if not match or cls in seen:raise ValueError('one explicit project semantic Test class')
        seen.add(cls)
        actual=[r for r in cases if r['class']==cls]
        if not actual or any(r['source']!=source or r['result']!='PASS_ORIGINAL_XML'for r in actual):raise ValueError('same-source genuine original semantic Test cases')
        modules={r.get('module')for r in actual}
        if len(modules)!=1 or not modules<={'protocol','storage','bootstrap','api','web','batch'}:raise ValueError('one explicit original XML module, never infer from package')
        module=next(iter(modules))
        path='src/schubert-nk-'+module+'/src/test/java/'+cls.replace('.','/')+'.java'
        if hashlib.sha256(read_source(path)).hexdigest()!=declaration['sourceSha256']:raise ValueError('exact declared current semantic Test source')
        if len({r['caseNameSha256']for r in actual})!=len(actual):raise ValueError('unique semantic case identity')
        result.extend(current_reference(r)for r in actual)
    return result


def main():
    qp,q=read_qualified();cp=qp.with_name('cases.json');cases=json.loads(cp.read_bytes())
    if len(cases)!=4040 or any(r['source']!=SOURCE or r['result']!='PASS_ORIGINAL_XML'for r in cases):raise ValueError('actual original4040 case identities')
    sp=BASE/'PG6268-outbox-failure-qualification-v1/manifest.json';selected=json.loads(sp.read_bytes())
    private=W/'pg6268-outbox-failure-qualification-v1/manifest.safe.json'
    if sha(sp)!='d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225'or sha(private)!=selected['privateManifestSha256']:raise ValueError('exact original current1350 inputs')
    proof=json.loads(private.read_bytes())
    if proof['source']!=SOURCE or proof['allPhysicalMainSha256']!=q['allPhysicalMainSha256']:raise ValueError('all1667 whole classes equal original static/selected')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:raise ValueError('all851 actual Main fixed')
    rows=load(INPUT,INPUT_SHA,SOURCE);priors={r['findingId']:r for r in load(PRIOR,PRIOR_SHA,OLD)}
    index={(r['class'],r['caseNameSha256']):r for r in cases}
    if len(index)!=4040:raise ValueError('one actual original case identity each')
    joined=[];counts=Counter();unresolved=[]
    snapshot=W/'pg6266-outbox-failure-selected-v1/source'
    for row in rows:
        value=copy.deepcopy(row)
        if row['status']=='NOT_REVIEWED_CURRENT_SOURCE':joined.append(value);continue
        pending=row['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING'
        old=priors[row['priorFindingId']]if pending else row;refs=[]
        for ref in old.get('currentWholeCaseRefs',[]):
            actual=index.get((ref['class'],ref['caseNameSha256']))
            if actual is None:raise ValueError('prior semantic Test must exist in current original whole')
            refs.append(current_reference(actual))
        if not refs:
            by_identity={}
            for ref in old.get('originalSelectedCaseRefs',[]):
                cls=ref['className'];path=snapshot/('src/schubert-nk-'+ref['module']+'/src/test/java')/(cls.replace('.','/')+'.java')
                names=source_case_candidates(path.read_text(),ref['method'])
                actual=[index[(cls,hashlib.sha256(n.encode()).hexdigest())]for n in names if(cls,hashlib.sha256(n.encode()).hexdigest())in index]
                if len(actual)!=1:raise ValueError('one actual case identity for each selected method')
                by_identity[(cls,actual[0]['caseNameSha256'])]=current_reference(actual[0])
            refs=list(by_identity.values())
        if not refs and old.get('plannedCurrentWholeCaseClasses'):
            refs=declared_class_references(old['plannedCurrentWholeCaseClasses'],cases,SOURCE,
                lambda path:subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT))
        context=old.get('staticContextPremiseOnly')is True and old.get('status')=='CONTEXT_NOT_APPLICABLE'
        if not refs and not context:
            value['wholeSourceQualifiedCaseBindingStillPending']=True
            unresolved.append(dict(findingId=row['findingId'],sourcePath=row['sourcePath'],reason='Missing authenticated semantic case remains pending; no Root/native/old success inferred'))
            joined.append(value);continue
        if pending:value['status']=row['priorDisposition']
        value.update(currentWholeCaseRefs=refs,currentWholeJoinPending=False,currentWholeSource=SOURCE,
            currentWholeSha256=sha(qp),currentWholeCasesSha256=sha(cp),staticContextPremiseOnly=context,
            historicalSuccessImported=False,formalAccepted=False,F03Accepted=False,ptAlternativeCompleted=0)
        counts['priorSourceClass'if pending else'currentIndividualReview']+=1
        counts['staticContextOnly'if context else'actualCurrentCaseRefs']+=1
        joined.append(value)
    if len(joined)!=1350 or [r['findingId']for r in joined]!=[r['findingId']for r in rows]:raise ValueError('all raw1350 IDs/order retained')
    validate_rationales(joined)
    value=dict(actualExit=0,source=SOURCE,rawFindings=1350,inventoryFile='findings.json',
        statusCounts=dict(Counter(r['status']for r in joined)),inputManifestPath=INPUT.relative_to(ROOT).as_posix(),inputManifestSha256=INPUT_SHA,
        currentWholeQualificationSha256=sha(qp),currentWholeCasesSha256=sha(cp),joined=dict(counts),unresolvedCaseBindings=unresolved,
        sameSourceOriginalWholeTests=4040,wholeRun='PG6272-six-v1',testsExecuted=0,additionalBuildsIssued=0,
        pmdRawRemoved=0,newAcceptedLeaves=0,formalAccepted=False,F03Accepted=False,ptAlternativeCompleted=0,effortPercent=None)
    os.umask(0o077);out=BASE/'PG6282-current4040-static-join-v1';out.mkdir()
    with(out/'findings.json').open('x')as f:json.dump(joined,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['inventorySha256']=sha(out/'findings.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,statusCounts=value['statusCounts'],joined=dict(counts),unresolvedCaseBindings=len(unresolved),manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
