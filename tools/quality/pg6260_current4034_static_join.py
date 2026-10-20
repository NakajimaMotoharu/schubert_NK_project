"""Join actual current whole case identities without importing historical PASS or inventing missing refs."""
import copy
import hashlib
import json
import os
from collections import Counter,defaultdict
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6258_current4034_trace import SOURCE,read_qualified
from pg6092_current3985_static_join import source_case_candidates
from static_disposition_overlay import load,validate_rationales

INPUT=BASE/'PG6256-outbox-static-review-v1/manifest.json'
INPUT_SHA='7cb42ad2b6081fceddbbaddfa8eca6a58082c5d999ce297872340a378c68e56c'


def current_reference(row):
    return {k:row[k]for k in ('testId','xmlSha256','class','caseNameSha256','source')}


def main():
    qp,q=read_qualified();cp=qp.with_name('cases.json');cases=json.loads(cp.read_bytes())
    if len(cases)!=4034 or any(r['source']!=SOURCE or r['result']!='PASS_ORIGINAL_XML'for r in cases):
        raise ValueError('all actual4034 case identities from original same-source whole')
    selected_path=BASE/'PG6248-normal-phase-qualification-v1/manifest.json';selected=json.loads(selected_path.read_bytes())
    private=W/'pg6248-normal-phase-qualification-v1/manifest.safe.json'
    if sha(selected_path)!='4495f3778a40c33c3de9f6fbd1082581fba8f7cf02caafae55687b32928b8bfe'or sha(private)!=selected['privateManifestSha256']:
        raise ValueError('actual unfiltered1343 analyzer/class inputs')
    proof=json.loads(private.read_bytes())
    if proof['source']!=SOURCE or proof['allPhysicalMainSha256']!=q['allPhysicalMainSha256']:
        raise ValueError('all1667 original whole classes equal original static/selected inputs')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:
        raise ValueError('currentMain fixed; no binding to a later source')
    rows=load(INPUT,INPUT_SHA,SOURCE);index={(r['class'],r['caseNameSha256']):r for r in cases}
    if len(index)!=4034:raise ValueError('one actual case identity each')
    by_class=defaultdict(list)
    for r in cases:by_class[r['class']].append(r)
    prior={}
    for old,path,digest in (
        ('acb5fe9c375ede57f5d15fc5fc392f2197c910d4','PG6124-current-static3988-v1/manifest.json','c100470dda47acbd15b7f586dc981b00d08eaeb560905fd8b0658d4efa24056b'),
        ('55109c74737208f906b69c04cd0931b466d2fadd','PG6226-consumer-static-review-v1/manifest.json','0c34986ca027b72dcbf3a652dac997724637a8749b91a7ee0c5590a9b88ffc44')):
        for row in load(BASE/path,digest,old):
            if row['status']in ('REQUIRED_CONTRACT','CONTEXT_NOT_APPLICABLE','FALSE_POSITIVE'):
                if row['findingId']in prior:raise ValueError('unambiguous prior review identity')
                prior[row['findingId']]=row
    snapshot=W/'pg6246-normal-phase-selected-v1/source'
    def refs_for_selected(refs):
        result={}
        for ref in refs:
            cls=ref['className'];path=snapshot/('src/schubert-nk-'+ref['module']+'/src/test/java')/(cls.replace('.','/')+'.java')
            names=source_case_candidates(path.read_text(),ref['method'])
            matches=[index[(cls,hashlib.sha256(n.encode()).hexdigest())]for n in names if(cls,hashlib.sha256(n.encode()).hexdigest())in index]
            if len(matches)!=1:raise ValueError('one real current method identity for each selected reference')
            actual=matches[0];result[(cls,actual['caseNameSha256'])]=current_reference(actual)
        return list(result.values())
    fresh_case_classes={
        'OutboxJmsSender':'dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest',
        'OutboxDispatcher':'dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest',
        'OwnedOutboxDispatcher':'dev.codex.schubert.nk.api.messaging.outbound.OwnedOutboxDispatcherTest',
        'WebLogDispatcher':'dev.codex.schubert.nk.web.logging.WebLogDispatcherTest'}
    joined=[];counts=Counter();unresolved=[]
    for row in rows:
        value=copy.deepcopy(row)
        if row['status']=='NOT_REVIEWED_CURRENT_SOURCE':joined.append(value);continue
        old=prior[row['priorFindingId']]if row['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING'else row
        refs=[]
        if old.get('currentWholeCaseRefs'):
            for ref in old['currentWholeCaseRefs']:
                actual=index.get((ref['class'],ref['caseNameSha256']))
                if actual is None:raise ValueError('historical semantic method missing from actual current whole')
                refs.append(current_reference(actual))
        elif old.get('originalSelectedCaseRefs'):refs=refs_for_selected(old['originalSelectedCaseRefs'])
        elif row['sourcePath'].rsplit('/',1)[-1][:-5]in fresh_case_classes:
            cls=fresh_case_classes[row['sourcePath'].rsplit('/',1)[-1][:-5]]
            if not by_class[cls]:raise ValueError('required actual current Outbox/log case class')
            refs=[current_reference(r)for r in by_class[cls]]
        context=old.get('staticContextPremiseOnly')is True and old['status']=='CONTEXT_NOT_APPLICABLE'
        if not refs and not context:
            value['wholeSourceQualifiedCaseBindingStillPending']=True
            unresolved.append(dict(findingId=row['findingId'],sourcePath=row['sourcePath'],reason='No authenticated current semantic Test reference; do not infer native/held-Main or transfer old success'))
            joined.append(value);continue
        if row['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING':value['status']=row['priorDisposition']
        value.update(currentWholeCaseRefs=refs,currentWholeJoinPending=False,currentWholeSource=SOURCE,
            currentWholeSha256=sha(qp),currentWholeCasesSha256=sha(cp),staticContextPremiseOnly=context,
            historicalSuccessImported=False,formalAccepted=False,F03Accepted=False,ptAlternativeCompleted=0)
        counts['sourceClassPrior'if 'priorFindingId'in row else'newIndividualReview']+=1
        counts['staticContextOnly'if context else'actualCurrentCaseRefs']+=1
        joined.append(value)
    if [r['findingId']for r in joined]!=[r['findingId']for r in rows]or len(joined)!=1343:raise ValueError('raw complete/no removed reordered findings')
    validate_rationales(joined)
    value=dict(actualExit=0,source=SOURCE,rawFindings=1343,statusCounts=dict(Counter(r['status']for r in joined)),
        inventoryFile='findings.json',inputManifestPath=INPUT.relative_to(ROOT).as_posix(),inputManifestSha256=INPUT_SHA,
        currentWholeQualificationSha256=sha(qp),currentWholeCasesSha256=sha(cp),joined=dict(counts),unresolvedCaseBindings=unresolved,
        sameSourceOriginalWholeTests=4034,wholeRun='PG6244-six-v1',testsExecuted=0,additionalBuildsIssued=0,
        pmdRawRemoved=0,newAcceptedLeaves=0,formalAccepted=False,F03Accepted=False,ptAlternativeCompleted=0,effortPercent=None)
    os.umask(0o077);out=BASE/'PG6260-current4034-static-join-v1';out.mkdir()
    with(out/'findings.json').open('x')as f:json.dump(joined,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['inventorySha256']=sha(out/'findings.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,statusCounts=value['statusCounts'],joined=dict(counts),unresolvedCaseBindings=len(unresolved),manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
