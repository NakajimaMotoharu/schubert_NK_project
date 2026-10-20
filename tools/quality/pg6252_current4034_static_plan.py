"""Exact current1343 inventory and two independent prior source/class rebindings, not acceptance."""
import json
import os
from collections import Counter
from types import FunctionType
import pg6124_current3988_static_join as previous
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6248_normal_phase_qualification import original_source
from static_disposition_overlay import load,validate_rationales


def calculate():
    source=original_source()
    qp=BASE/'PG6248-normal-phase-qualification-v1/manifest.json'
    if sha(qp)!='4495f3778a40c33c3de9f6fbd1082581fba8f7cf02caafae55687b32928b8bfe':raise ValueError('actual original113 source/static qualification')
    q=json.loads(qp.read_bytes());private=W/'pg6248-normal-phase-qualification-v1/manifest.safe.json'
    rawpath=private.with_name('findings.safe.json')
    if sha(private)!=q['privateManifestSha256']or sha(rawpath)!=q['findingsSha256']:raise ValueError('all original exact static/class/source inputs')
    proof=json.loads(private.read_bytes());raw=json.loads(rawpath.read_bytes())
    if proof['source']!=source or proof['actualExit']!=0 or len(raw)!=1343:raise ValueError('actual unfiltered current1343')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:raise ValueError('fixed all851 currentMain')
    strict=FunctionType(previous.strict_pending.__code__,{**vars(previous),'SOURCE':source})
    sources=(
        ('acb5fe9c375ede57f5d15fc5fc392f2197c910d4','PG6124-current-static3988-v1/manifest.json',
            'c100470dda47acbd15b7f586dc981b00d08eaeb560905fd8b0658d4efa24056b','PG6118-current3988-cases/qualification.json'),
        ('55109c74737208f906b69c04cd0931b466d2fadd','PG6226-consumer-static-review-v1/manifest.json',
            '0c34986ca027b72dcbf3a652dac997724637a8749b91a7ee0c5590a9b88ffc44','PG6212-current4027-cases/qualification.json'))
    rows=None;bindings=[]
    for oldsource,path,digest,physicalpath in sources:
        old=load(BASE/path,digest,oldsource)
        before=json.loads((BASE/physicalpath).read_bytes())['allPhysicalMainSha256']
        current,priors=strict(old,before,raw,proof['allPhysicalMainSha256'])
        if rows is None:rows=current
        else:
            for i,row in enumerate(current):
                if row['status']!='SOURCE_REBOUND_CURRENT_WHOLE_PENDING':continue
                if rows[i]['status']!='NOT_REVIEWED_CURRENT_SOURCE':raise ValueError('no duplicate prior disposition/fee credit')
                rows[i]=row
        bindings.append(dict(source=oldsource,manifestPath=(BASE/path).relative_to(ROOT).as_posix(),manifestSha256=digest,
            priorPhysicalSha256=sha(BASE/physicalpath),previousDecided=sum(r['status']in previous.bind_one.__globals__['ALLOWED']for r in old),strictReboundPending=len(priors)))
    if [r['findingId']for r in rows]!=[r['findingId']for r in raw]:raise ValueError('all raw identities and order unchanged')
    validate_rationales(rows)
    scope={}
    for row in rows:
        item=scope.setdefault(row['sourcePath'],dict(raw=0,pending=0,notReviewed=0,rules=Counter()))
        item['raw']+=1;item['rules'][row['rule']]+=1
        item['pending'if row['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING'else'notReviewed']+=1
    value=dict(actualExit=0,source=source,purpose='CURRENT_SOURCE_CLASS_REAUTHENTICATION_WHOLE_PENDING',
        rawFindings=len(raw),statusCounts=dict(Counter(r['status']for r in rows)),priorBindings=bindings,
        originalSelectedTests=113,originalSelectedQualificationSha256=sha(qp),originalRawFindingsSha256=sha(rawpath),
        inventoryFile='findings.json',reviewScopes=scope,newReviewedFindings=0,newAcceptedLeaves=0,
        currentWholeJoinPending=True,currentWholeCaseRefs=[],originalWholeRun='PG6244-six-v1',originalWholeTerminalConfirmed=False,
        formalAccepted=False,F03Accepted=False,nativeQualified=False,ptAlternativeCompleted=0,
        testsExecuted=0,additionalBuildsIssued=0,effortPercent=None)
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=BASE/'PG6252-current4034-static-plan-v1';out.mkdir()
    with(out/'findings.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['inventorySha256']=sha(out/'findings.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,source=value['source'],raw=value['rawFindings'],statusCounts=value['statusCounts'],
        priorBindings=value['priorBindings'],manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
