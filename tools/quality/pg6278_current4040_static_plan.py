"""Reauthenticate prior applicability only; retain fourteen unresolved case bindings."""
import copy
import json
import os
from collections import Counter
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6268_outbox_failure_qualification import original_source
from pg6124_current3988_static_join import strict_pending
from pg5910_storage_static_rebind import ordered_pairs
from pg5758_static_rebind import bind_one
from static_disposition_overlay import load,validate_rationales,DECIDED

PRIOR=BASE/'PG6260-current4034-static-join-v1/manifest.json'
PRIOR_SHA='3ce6a5270bce5df85fe80896ad5222efa96e5008a928846a28c7b9904a821771'
OLD='97dd2ba6185143632439f32dfc1d663061f1e55c'


def calculate():
    source=original_source();old=load(PRIOR,PRIOR_SHA,OLD)
    qp=BASE/'PG6268-outbox-failure-qualification-v1/manifest.json'
    if sha(qp)!='d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225':raise ValueError('original selected51/static qualification')
    q=json.loads(qp.read_bytes());private=W/'pg6268-outbox-failure-qualification-v1/manifest.safe.json'
    rawp=private.with_name('findings.safe.json')
    if sha(private)!=q['privateManifestSha256']or sha(rawp)!=q['findingsSha256']:raise ValueError('exact original all static/source/class bytes')
    proof=json.loads(private.read_bytes());raw=json.loads(rawp.read_bytes())
    if proof['source']!=source or proof['actualExit']!=0 or len(raw)!=1350:raise ValueError('current unfiltered1350')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:raise ValueError('all851 Main fixed during whole')
    beforep=BASE/'PG6244-current4034-cases/qualification.json'
    if sha(beforep)!='129f400938285f04cb016292b8e0822835f22d67bf3f899ec2f6e6b7b23004e9':raise ValueError('prior all1667 original physical map')
    before=json.loads(beforep.read_bytes())['allPhysicalMainSha256'];now=proof['allPhysicalMainSha256']
    rows,priors=strict_pending(old,before,raw,now)
    pairs=ordered_pairs(old,raw);held=0
    for i,row in enumerate(raw):
        pair=pairs.get(row['findingId']);prior=pair[0]if pair else None
        if prior is None or prior['status']!='SOURCE_REBOUND_CURRENT_WHOLE_PENDING':continue
        if not prior.get('wholeSourceQualifiedCaseBindingStillPending')or prior['priorDisposition']not in DECIDED:raise ValueError('only explicit prior unresolved case bindings')
        candidate=copy.deepcopy(prior);candidate['status']=prior['priorDisposition']
        value,kind=bind_one(row,[candidate],(ROOT/row['sourcePath']).read_bytes(),before,now)
        if kind!='REBOUND'or rows[i]['status']!='NOT_REVIEWED_CURRENT_SOURCE':raise ValueError('pending site must independently retain identical source/class family')
        value.update(wholeSourceQualifiedCaseBindingStillPending=True,
            priorUnresolvedReviewManifestSha256=PRIOR_SHA,priorUnresolvedFindingId=prior['findingId'],
            unresolvedReason='Prior missing semantic case remains unresolved; reauthentication is not acceptance')
        rows[i]=value;held+=1
    if held!=14:raise ValueError('all fourteen unresolved sites preserved, no promotion')
    for row in rows:
        if row['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING':
            row.update(priorReviewSource=OLD,priorReviewManifestSha256=PRIOR_SHA,
                currentPhysicalProofSha256=sha(private),formalAccepted=False,F03Accepted=False)
    if [r['findingId']for r in rows]!=[r['findingId']for r in raw]:raise ValueError('all raw IDs/order retained')
    validate_rationales(rows)
    value=dict(actualExit=0,source=source,rawFindings=len(raw),inventoryFile='findings.json',
        statusCounts=dict(Counter(r['status']for r in rows)),priorManifestPath=PRIOR.relative_to(ROOT).as_posix(),
        priorManifestSha256=PRIOR_SHA,priorWholeQualificationSha256=sha(beforep),
        originalSelectedQualificationSha256=sha(qp),originalRawFindingsSha256=sha(rawp),
        strictReboundPriorDecided=len(priors),priorUnresolvedRetained=held,newReviewedFindings=0,
        currentWholeJoinPending=True,currentWholeCaseRefs=[],testsExecuted=0,additionalBuildsIssued=0,
        pmdRawRemoved=0,newAcceptedLeaves=0,formalAccepted=False,F03Accepted=False,ptAlternativeCompleted=0,effortPercent=None)
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=BASE/'PG6278-current4040-static-plan-v1';out.mkdir()
    with(out/'findings.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['inventorySha256']=sha(out/'findings.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,statusCounts=value['statusCounts'],priorUnresolvedRetained=14,manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
