"""Strict current-source/class reauthentication plan; no new disposition or whole PASS claim."""
import json
import os
import subprocess
from collections import Counter
from types import FunctionType
import pg6124_current3988_static_join as previous
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6193_management_primary_qualification_v2 import original_source
from static_disposition_overlay import load, validate_rationales

OLD='acb5fe9c375ede57f5d15fc5fc392f2197c910d4'


def calculate():
    source=original_source()
    old=load(BASE/'PG6124-current-static3988-v1/manifest.json',
        'c100470dda47acbd15b7f586dc981b00d08eaeb560905fd8b0658d4efa24056b',OLD)
    qpath=BASE/'PG6193-management-primary-qualification-v2/manifest.json'
    if sha(qpath)!='e64ddbb2f3f2d736379f374633d00efa215872b3aaee344f1b43605002ad0e1f':raise ValueError('immutable original60/static qualification')
    q=json.loads(qpath.read_bytes());private=W/'pg6193-management-primary-qualification-v2/manifest.safe.json'
    rawpath=private.with_name('findings.safe.json')
    if sha(private)!=q['privateManifestSha256'] or sha(rawpath)!=q['findingsSha256']:raise ValueError('all original current static/class/source inputs')
    proof=json.loads(private.read_bytes());raw=json.loads(rawpath.read_bytes())
    if proof['source']!=source or len(raw)!=1334 or proof['actualExit']!=0:raise ValueError('actual unfiltered current raw1334')
    if {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:raise ValueError('fixed all851 source')
    before=json.loads((BASE/'PG6118-current3988-cases/qualification.json').read_bytes())['allPhysicalMainSha256']
    rows,priors=FunctionType(previous.strict_pending.__code__,{**vars(previous),'SOURCE':source})(old,before,raw,proof['allPhysicalMainSha256'])
    if [r['findingId'] for r in rows]!=[r['findingId'] for r in raw]:raise ValueError('complete raw identity/order retained')
    validate_rationales(rows)
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--',':(glob)src/*/src/main/java/**/*.java'],cwd=ROOT,text=True).splitlines())
    scopes=[]
    for path in sorted(changed):
        oldrows=[r for r in old if r['sourcePath']==path];new=[r for r in raw if r['sourcePath']==path]
        scopes.append(dict(path=path,sourceSha256=proof['allSourceHashes'][path],previousRaw=len(oldrows),
            previousStatusCounts=dict(Counter(r['status'] for r in oldrows)),currentRaw=len(new),
            currentRules=dict(Counter(r['rule'] for r in new)),findingIds=[r['findingId'] for r in new]))
    if len(changed)!=13 or sum(s['currentRaw'] for s in scopes)!=190 or len(priors)!=628:
        raise ValueError('exact current grouped review needs, no silent classification')
    value=dict(actualExit=0,source=source,purpose='PLAN_SOURCE_REAUTHENTICATION_CURRENT_WHOLE_PENDING',
        rawFindings=1334,statusCounts=dict(Counter(r['status'] for r in rows)),
        previousSource=OLD,previousDecided=729,strictSourceClassReboundPending=628,
        previousDecisionsInvalidatedForRereview=101,changedSources=13,changedSourceFindings=190,
        reviewScopes=scopes,inventoryFile='findings.json',newReviewedFindings=0,newAcceptedLeaves=0,
        originalSelectedTests=60,originalSelectedQualificationSha256=sha(qpath),
        originalRawFindingsSha256=sha(rawpath),currentWholeCaseRefs=[],currentWholeJoinPending=True,
        originalWholeRun='PG6196-six-v1',originalWholeTerminalConfirmed=False,
        formalAccepted=False,F03Accepted=False,nativeQualified=False,ptAlternativeCompleted=0,
        testsExecuted=0,additionalBuildsIssued=0,effortPercent=None)
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=BASE/'PG6200-current4024-static-plan-v1';out.mkdir()
    with (out/'findings.json').open('x') as f:
        json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['inventorySha256']=sha(out/'findings.json')
    with (out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k] for k in ('source','rawFindings','statusCounts','strictSourceClassReboundPending','previousDecisionsInvalidatedForRereview','changedSources','changedSourceFindings','newReviewedFindings')}|dict(manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
