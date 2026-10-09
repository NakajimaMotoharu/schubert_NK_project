"""Emit a patch for one existing completion owner; preserve historical969 counters and budgets."""
import difflib
import hashlib
import json
from pathlib import Path
from pg747_wbs_candidate import transform

T=Path(__file__).resolve().parents[4]
B=T/'documents/400_PGPT/470_PMO'
CHANGED='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner.java'


if __name__=='__main__':
    p=B/'485_WBS網羅性・受入対応.json';old=p.read_text();seen=[]
    def change(a):
        if a.get('path')!=CHANGED:return False
        assert a['owner']==a['costOwner']=='WBS-P017-12';seen.append(a['path'])
        a['previousCandidateSha256']=a['sha256'];a['sha256']=hashlib.sha256((T/CHANGED).read_bytes()).hexdigest()
        a['candidateProvenance']={'candidateSource':'c035e90ee759fffcfdf070e0a069e977b61d0b54','baselineSource':'8d4b68b4f1449932ebe506aaf08e584bbfea8dd2','decision':'SSC237','evidence':'PG791/793 selected96/staticbatch0; fresh full/native pending','state':'HOST_LIMITED_NOT_DEPLOYED','accepted':False,'newOuterArtifacts':0,'newNestedTypes':4,'commonCostOwnerOnly':'WBS-P017-12'}
        return True
    new=transform(old,change);assert seen==[CHANGED]
    changes={p:(old,new)};p=B/'486_WBS現行実績.json';old=p.read_text();prior=json.loads(old)['inventorySha256']
    assert old.count(prior)==1;changes[p]=(old,old.replace(prior,hashlib.sha256(new.encode()).hexdigest()))
    print('*** Begin Patch')
    for p,(old,new)in changes.items():
        print('*** Update File: '+str(p))
        for line in list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=1))[2:]:print('@@'if line.startswith('@@')else line)
    print('*** End Patch')
