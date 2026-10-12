"""Immutable new-only tools and signed public input transport, not candidate placement."""
import hashlib
import inspect
import json
import os
import subprocess
import pg1513_original_component_stage as prior
from pg1446_current_cold_stage import SSH, W, P
from pg1536_pending_candidate_sources import TOOLS

def main():
    os.umask(0o077)
    frozen=json.loads((W/'pg1537-pending-unused-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0:raise ValueError('fixed operator compile required')
    raw=inspect.getsource(prior.main).replace('pg1513-original-component-stage-v1','pg1538-pending-unused-stage-v1').replace('PG1513-original-component-stage-v1','PG1538-pending-unused-stage-v1').replace('pg1512-original-component-frozen-v1.safe.json','pg1537-pending-unused-frozen-v1.safe.json')
    namespace={**prior.__dict__,'TOOLS':TOOLS};exec(compile(raw,'<new-only current partial-original tools stage>','exec'),namespace)
    result=namespace['main']()
    if result not in [None,0]:raise ValueError('immutable tool stage failed')
    remote='/home/ubuntu/pg1538-candidate-input-v1'
    archive=P/'pg1538-release-v1.tar';sig=P/'pg1535-manifest-v1.sig';bundle=W/TOOLS/'bundle.safe.json'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=frozen['archiveSha256'] or hashlib.sha256(bundle.read_bytes()).hexdigest()!=frozen['bundleSha256']:
        raise ValueError('fixed input archive or bundle changed')
    log=W/'pg1538-candidate-input-stage-v1.private.log'
    with log.open('xb')as f:
        r=subprocess.run(SSH+['test ! -e '+remote+' && sudo -n test ! -e /opt/schubert-nk/releases/0.1.0-PG1535 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg1535-manifest.sig && mkdir -m700 '+remote],stdout=f,stderr=f,check=True)
        options=['-q','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(P/'known_hosts'),'-i',str(P/'vm-access'),'-P','22222']
        r=subprocess.run(['scp',*options,str(archive),str(sig),str(bundle),'ubuntu@127.0.0.1:'+remote+'/'],stdout=f,stderr=f,check=True)
        f.flush();os.fsync(f.fileno())
    value={'run':'PG1538-signed-input-stage-v1','actualExit':r.returncode,'candidatePlacementIssued':False,'currentApprovalEpochUnitDbMutation0':True,'archiveSha256':frozen['archiveSha256'],'bundleSha256':frozen['bundleSha256'],'formalAccepted':False}
    with(W/'pg1538-signed-input-stage-v1.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return value['actualExit']

if __name__=='__main__':raise SystemExit(main())
