"""Public681/683/684/685 independent selected manifests; no private payload export."""
import hashlib
import json
import os
import subprocess
from pg1625_unsupported_ports_selected import W, ROOT
from pg1719_current_bootstrap_sources import SOURCE

GROUPS=[('681','018_NK-OPS-001','pg1716-formatted-api-configuration-selected-v1','pg1717-formatted-api-selected-qualified-v1','1716',5,['OPS-API-MAIN-001','OPS-API-MAIN-002','OPS-API-MAIN-003','OPS-API-MAIN-004','OPS-API-MAIN-005']),
 ('683','017_NK-BAT-001','pg1739-successful-backup-fault-selected-v1','pg1740-successful-projection-qualified-v1','1739',7,['MDB-PROJ-1737-'+f'{i:03}' for i in range(1,8)]),
 ('684','018_NK-OPS-001','pg1743-root-generation-boundaries-selected-v1','pg1745-root-exact-qualified-v1','1743',8,['ROOTGEN-1741-'+f'{i:03}' for i in range(1,9)]),
 ('685','018_NK-OPS-001','pg1746-caddy-address-selected-v1','pg1747-caddy-exact-qualified-v1','1746',2,['CADDY-1746-001','CADDY-1746-002'])]

def main():
    os.umask(0o077)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for number,program,selected,qualified,run,count,ids in GROUPS:
        records={}; values={}
        for label,name in [('selected',selected),('qualified',qualified)]:
            p=W/name/'manifest.safe.json'; raw=p.read_bytes(); v=json.loads(raw)
            if v.get('actualExit')!=0: raise ValueError('actual success required')
            records[label]={'path':name+'/manifest.safe.json','sha256':hashlib.sha256(raw).hexdigest(),'actualExit':0,'serverManifestSha256':v['manifestSha256']}; values[label]=v
        s=values['selected']; q=values['qualified']
        if s['tests']!=count or q['testsByRun']!={run:count} or s['productionSource']!=SOURCE or s['classByteMismatch']!=0 or s['FESAbortedNotRun']!=0 or q['remaining']!=s['remaining']:
            raise ValueError('current exact unique qualified count/CRC required')
        result={'program':program,'testIds':ids,'branch':'dev-foundation','collectorCommit':head,'productionSource':SOURCE,'testSource':s.get('testSource'),'records':records,'actualExit':0,'finalSelectedTests':count,'historicalCountsNotAdded':True,'FESAbortedNotRun':0,'warnings':0,'classByteMismatch':0,'vmOperations':0,'coverageRemaining':s['remaining'],'coverage100':False,'environment':{'execution':'pinned dedicated LAN Ubuntu26.04/x86_64','jdk':'25.0.4','junitJupiter':'5.13.4','junitPlatform':'1.13.4','jacoco':'0.8.15'},'command':'python3 -B tools/quality/<corresponding fixed selected and qualification tools>','independentOracle':'explicit literal expectations and exact unique XML IDs; qualification never reexecutes tests','privateRawExported':False,'formalAccepted':False,'formalRun':'PT-WEB-20260925-24','formalTests':1964,'formalScopes':53,'wholeLeafAcceptedDelta':0,'N':None,'T':None,'actualAllocatedPp':None}
        out=ROOT/'evidence/01_PT'/program/'evidence/output'/(number+'_manifest.json')
        with out.open('x') as f: json.dump(result,f,sort_keys=True,indent=2);f.flush();os.fsync(f.fileno())
        print(json.dumps({'number':number,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))

if __name__=='__main__':main()
