"""Fresh quiescent data observation after full recovery; no admission/start/stop/ACK authority."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
import pg4168_retained_pair_keeper as previous

SLOT='pg4210-quiescent-current-read-v1'


def payload():
    raw=previous.payload();raw=raw[:raw.index('import time,signal,select,ctypes,dbus,traceback')]
    raw=raw.replace("save=base/('pg4180-retained-pair-keeper-v1-'+MODE)","save=base/'"+SLOT+"'")
    return raw+'\n'+BODY


BODY=r'''
signed={};exec(SIGNED_SOURCE,signed)
materials=[{'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [pin,signature]]
require(signed['verify'](str(root),data['artifacts'],raw,materials)is True)
before_raw=Path('/var/lib/pgpt-s1-preservation/pg4186-partial-independent-post-v1/after.private.json').read_bytes()
require(hashlib.sha256(before_raw).hexdigest()=='e77657150336362b6010058384db9d8a71be650b99c9b7c688c67b1cc862746c');before=json.loads(before_raw)
for pid in [696557,790010,789928,791348]:require(not(Path('/proc')/str(pid)).exists())
current=snapshot();require(not current['actors']and not current['flocks']and not current['database']['locks']and not current['database']['peers'])
same={k:current[k]==before[k]for k in ['durable','native','startup','runtime']};same['all24']=current['database']['rows']==before['database']['rows'];require(all(same.values()))
for unit,v in current['units'].items():require(v['MainPID']==v['ControlPID']=='0'and not v['Job'])
configurations=config();require(set(configurations)==set(old['configuration'])and all(CONFIG_CONTRACT['same'](old['configuration'][u],v,exec_record)for u,v in configurations.items()))
require(current==snapshot())
encoded=json.dumps({'current':current,'configuration':configurations},sort_keys=True).encode()
with(save/'observed.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
value={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'privateSha256':hashlib.sha256(encoded).hexdigest(),'same':same,'allTenNoProcessOrJob':True,'allDbPeerAdvisoryFlock0':True,
 'unitRuntimeChangedFields':{u:[k for k,v in now.items()if v!=before['units'][u].get(k)]for u,now in current['units'].items()if now!=before['units'][u]},
 'all32DeclarationsSame':True,'nativeFiles':sum(p.endswith('.exec')for p in current['native']),'startupEntriesWithoutDirectory':len(current['startup'])-1,
 'authorityIssued':False,'stateChangingActions':0,'formalAccepted':False}
(save/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))
'''


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload();compile(raw,'<quiescent read>','exec');(out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-','proof'],input=raw.encode(),capture_output=True,timeout=180)
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e'}
    if r.returncode==0:value['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
