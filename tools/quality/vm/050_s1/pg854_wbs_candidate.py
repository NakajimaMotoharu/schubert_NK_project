"""Emit only actual SSC240 three existing candidate hashes; no acceptance credit."""
import difflib, hashlib, json
from pathlib import Path
from pg747_wbs_candidate import transform
T = Path(__file__).resolve().parents[4]
B = T/'documents/400_PGPT/470_PMO'
OWNERS = {'MaintenanceRunFiles': 'WBS-P004-03', 'MorningNewRunAdmission': 'WBS-P017-02', 'MorningResumeAdmission': 'WBS-P017-02'}
if __name__ == '__main__':
    p = B/'485_WBS網羅性・受入対応.json'; old=p.read_text(); seen=[]
    def change(a):
        name=Path(a.get('path', '')).stem
        if name not in OWNERS or '/src/main/java/' not in a['path']: return False
        assert a['owner'] == a['costOwner'] == OWNERS[name]; seen.append(name)
        a['previousCandidateSha256']=a['sha256']; a['sha256']=hashlib.sha256((T/a['path']).read_bytes()).hexdigest()
        a['candidateProvenance']={'decision':'SSC240','baselineSource':'2a0d5aa392c85a1dc12a1cdb423978e8500895b8','state':'UNTESTED_NOT_DEPLOYED','evidence':'PG853 old-source sameSession reproduction0; candidate854 pending','accepted':False,'newOuterArtifacts':0,'commonCostOwnerOnly':OWNERS[name]}
        return True
    new=transform(old,change); assert set(seen)==set(OWNERS)
    changes={p:(old,new)}; p=B/'486_WBS現行実績.json'; old=p.read_text(); prior=json.loads(old)['inventorySha256']
    assert old.count(prior)==1; changes[p]=(old,old.replace(prior,hashlib.sha256(new.encode()).hexdigest()))
    print('*** Begin Patch')
    for p,(old,new) in changes.items():
        print('*** Update File: '+str(p))
        for line in list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=1))[2:]: print('@@' if line.startswith('@@') else line)
    print('*** End Patch')
