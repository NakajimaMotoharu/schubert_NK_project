"""Exact raw1357/source-class reauthentication; fourteen unresolved bindings remain held."""
import copy
import json
import os
from collections import Counter
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6298_web_send_qualification import original_source
from pg6124_current3988_static_join import strict_pending
from pg5910_storage_static_rebind import ordered_pairs
from pg5758_static_rebind import bind_one
from static_disposition_overlay import load,validate_rationales,DECIDED

PRIOR=BASE/'PG6282-current4040-static-join-v1/manifest.json'
PRIOR_SHA='661551cbfc5cabdd2606b91fd9a6c0290c45b3f8f8fe5306f44dce6ac4167144'
OLD='b4230118efcc429ee29d6e6f5761c55175f1e85e'


def calculate():
    source=original_source();old=load(PRIOR,PRIOR_SHA,OLD)
    qp=BASE/'PG6298-web-send-qualification-v1/manifest.json'
    if sha(qp)!='00b8f41991bf05c2aaf439cc502ecf6afba47f9247587684941ee168dbc75c27':raise ValueError('original selected84/static qualification')
    q=json.loads(qp.read_bytes());private=W/'pg6298-web-send-qualification-v1/manifest.safe.json';rawp=private.with_name('findings.safe.json')
    if sha(private)!=q['privateManifestSha256']or sha(rawp)!=q['findingsSha256']:raise ValueError('original all static/source/class inputs')
    proof=json.loads(private.read_bytes());raw=json.loads(rawp.read_bytes())
    if proof['source']!=source or proof['actualExit']!=0 or len(raw)!=1357:raise ValueError('current unfiltered1357')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:raise ValueError('all851 Main fixed during whole')
    beforep=BASE/'PG6272-current4040-cases/qualification.json'
    if sha(beforep)!='dc3e2e9b2cb435307b3c248964452e93dfc008a23a69072d8d4e9046dec8eed5':raise ValueError('prior original all1667 physical map')
    before=json.loads(beforep.read_bytes())['allPhysicalMainSha256'];now=proof['allPhysicalMainSha256']
    rows,priors=strict_pending(old,before,raw,now);pairs=ordered_pairs(old,raw);held=0
    for i,row in enumerate(raw):
        pair=pairs.get(row['findingId']);prior=pair[0]if pair else None
        if prior is None or prior['status']!='SOURCE_REBOUND_CURRENT_WHOLE_PENDING':continue
        if not prior.get('wholeSourceQualifiedCaseBindingStillPending')or prior['priorDisposition']not in DECIDED:raise ValueError('explicit prior unresolved sites only')
        candidate=copy.deepcopy(prior);candidate['status']=prior['priorDisposition']
        value,kind=bind_one(row,[candidate],(ROOT/row['sourcePath']).read_bytes(),before,now)
        if kind!='REBOUND'or rows[i]['status']!='NOT_REVIEWED_CURRENT_SOURCE':raise ValueError('unresolved source/family must independently remain identical')
        value.update(wholeSourceQualifiedCaseBindingStillPending=True,priorUnresolvedReviewManifestSha256=PRIOR_SHA,
            priorUnresolvedFindingId=prior['findingId'],unresolvedReason='Prior missing semantic Test remains unresolved; no native/Root authority inferred')
        rows[i]=value;held+=1
    if held!=14:raise ValueError('all fourteen unresolved sites retained, no promotion')
    for row in rows:
        if row['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING':row.update(priorReviewSource=OLD,priorReviewManifestSha256=PRIOR_SHA,
            currentPhysicalProofSha256=sha(private),formalAccepted=False,F03Accepted=False)
    if [r['findingId']for r in rows]!=[r['findingId']for r in raw]:raise ValueError('raw IDs/order retained')
    validate_rationales(rows)
    value=dict(actualExit=0,source=source,rawFindings=1357,inventoryFile='findings.json',statusCounts=dict(Counter(r['status']for r in rows)),
        priorManifestPath=PRIOR.relative_to(ROOT).as_posix(),priorManifestSha256=PRIOR_SHA,priorWholeQualificationSha256=sha(beforep),
        originalSelectedQualificationSha256=sha(qp),originalRawFindingsSha256=sha(rawp),strictReboundPriorDecided=len(priors),
        priorUnresolvedRetained=held,newReviewedFindings=0,currentWholeJoinPending=True,currentWholeCaseRefs=[],
        testsExecuted=0,additionalBuildsIssued=0,pmdRawRemoved=0,newAcceptedLeaves=0,formalAccepted=False,F03Accepted=False,
        ptAlternativeCompleted=0,effortPercent=None)
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=BASE/'PG6308-current4043-static-plan-v1';out.mkdir()
    with(out/'findings.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['inventorySha256']=sha(out/'findings.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,statusCounts=value['statusCounts'],strictReboundPriorDecided=len([r for r in rows if r['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING'])-14,priorUnresolvedRetained=14,manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
