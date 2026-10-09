"""Emit existing three artifact host qualification only; no acceptance/counter reclassification."""
import difflib,hashlib,json
from pathlib import Path
from pg747_wbs_candidate import transform
T=Path(__file__).resolve().parents[4];B=T/'documents/400_PGPT/470_PMO'
OWNERS={'MaintenanceRunFiles':'WBS-P004-03','MorningNewRunAdmission':'WBS-P017-02','MorningResumeAdmission':'WBS-P017-02'}
if __name__=='__main__':
    p=B/'485_WBS網羅性・受入対応.json';old=p.read_text();seen=[]
    def edit(a):
        n=Path(a.get('path','')).stem
        if n not in OWNERS or '/src/main/java/' not in a['path']:return False
        assert a['owner']==a['costOwner']==OWNERS[n]
        assert a['sha256']==hashlib.sha256((T/a['path']).read_bytes()).hexdigest();seen.append(n)
        a['candidateProvenance']={'candidateSource':'e01612fcd7f2752df5ae0836b78538fd5e87f120','baselineSource':'2a0d5aa392c85a1dc12a1cdb423978e8500895b8','decision':'SSC240','evidence':'PG854v4 selected98/staticbatch0; PG857/858 fresh3541/522/static6zero; manifestfcc7df91…; signed862 not deployed','state':'HOST_QUALIFIED_NOT_DEPLOYED','accepted':False,'newOuterArtifacts':0,'commonCostOwnerOnly':OWNERS[n],'newNativePending':True,'global100':False}
        return True
    new=transform(old,edit);assert set(seen)==set(OWNERS);changes={p:(old,new)}
    p=B/'486_WBS現行実績.json';old=p.read_text();prior=json.loads(old)['inventorySha256'];assert old.count(prior)==1
    changes[p]=(old,old.replace(prior,hashlib.sha256(new.encode()).hexdigest()))
    print('*** Begin Patch')
    for p,(old,new)in changes.items():
        print('*** Update File: '+str(p))
        for l in list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=1))[2:]:print('@@'if l.startswith('@@')else l)
    print('*** End Patch')
