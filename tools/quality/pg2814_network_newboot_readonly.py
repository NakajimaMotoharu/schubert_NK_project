"""Fresh cold source042 DB/durable/signature/Unit proof from sealed completed data only.

SS343353/SSC264, PT-OPS-2814. Old b2d6 owner/permit/tmpfs/native is not restored.
"""
import hashlib
import json
import os
from pathlib import PurePosixPath
import subprocess
from pg1446_current_cold_stage import W,SSH,P
from pg1674_critical_management_gate import management_gate
import pg2206_outage_cold_reauthentication_v2 as prior

SLOT='pg2814-network-newboot-readonly-v2'
SOURCE='04207efc3ad78bca75942153a90c70985064c988'
BOM='552c5e25591483ee2c9aa95c6b8170f37e3390b14bd08ed88bfc0c4870002a37'
BOOT='79a3260a-e16d-42bf-942a-b914ed144c28'
BEFORE='5ebddf83bca971ab57168384c0d3e6bac4ec2fb1e6c0997fdb1e737e04694739'


def one(raw,old,new):
    if raw.count(old)!=1:raise ValueError('one exact cold semantic input boundary required')
    return raw.replace(old,new)


def unit_vectors(values):
    if type(values)is not dict or not values:raise ValueError('sealed Unit vector inventory required')
    result={}
    for name,value in values.items():
        if (type(name)is not str or not name.startswith('/')or str(PurePosixPath(name))!=name
            or '..'in PurePosixPath(name).parts or any(ord(c)<32 for c in name)
            or type(value)is not list or len(value)!=10
            or any(type(v)is not int or v<0 for v in value[:9])
            or type(value[9])is not str or len(value[9])!=64 or set(value[9])-set('0123456789abcdef')):
            raise ValueError('exact nine metadata plus SHA256 sealed Unit vector required')
        result[name]={'metadata':value[:9],'sha256':value[9]}
    return result


def payload():
    raw=prior.payload()
    raw=one(raw,'SOURCE='+repr(prior.prior.SOURCE),'SOURCE='+repr(SOURCE))
    raw=one(raw,'BOM='+repr(prior.prior.BOM),'BOM='+repr(BOM))
    raw=one(raw,'SEALED='+repr(prior.prior.SEALED),'SEALED='+repr(BEFORE))
    raw=raw.replace(prior.SLOT,SLOT).replace('0.1.0-PG2126','0.1.0-PG2654').replace('pg2126-manifest.sig','pg2654-manifest.sig')
    old="raw=(BASE/'pg2186-newsource-full-live-seal-v1/before.private.json').read_bytes()\nrequire(hashlib.sha256(raw).hexdigest()==SEALED)\nold=json.loads(raw);require(old['source']==SOURCE and old['manifestSha256']==BOM)"
    new="""raw=(BASE/'pg2806-current-042-before-v1/before.private.json').read_bytes()
require(hashlib.sha256(raw).hexdigest()==SEALED)
saved=json.loads(raw)
require(set(saved)=={'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units'})
# Completed prior-boot data is only an immutable independent oracle; tmpfs and ownership are not reused.
old={'source':SOURCE,'manifestSha256':BOM,'rows':saved['rows'],'units':saved['units'],
 'configuration':saved['configuration'],'unitFiles':unit_vectors(saved['unitFilesActual']),
 'durable':{'originals':saved['originals'],'backup':saved['backup'],**saved['extraDurable']}}
"""
    raw=one(raw,old,new)
    import inspect
    raw='from pathlib import PurePosixPath\n'+inspect.getsource(unit_vectors)+'\n'+raw
    raw=one(raw,"datname='schubert_nk'and usename in('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector')",
        "datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid()")
    raw=one(raw,"require(boot!='3d69f5af-6bac-46b1-a540-7591c4a79a0d')","require(boot=="+repr(BOOT)+" and boot!='b2d6f605-61cf-425f-8fbd-12d606f6ee66')")
    marker=" require(peers.splitlines()==[b'0',b'0'])"
    extra="""
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;m=metadata(p)
  require(m[2:7]==[0,0,stat.S_IFREG|0o600,1,0]and not os.listxattr(p))
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(m[0]),os.minor(m[0]),m[1]))
  require(m==metadata(p))
"""
    raw=one(raw,marker,marker+extra)
    raw=one(raw,"'oldRunPermitNativeRestored':False","'oldRunPermitNativeRestored':False,'newLocksNoFlockTwice':True,'oldTmpfsComparedAsPersistent':False")
    from pyflakes.api import check
    if check(raw,'<source042 newboot full read-only>'):raise ValueError('whole cold namespace required')
    compile(raw,'<newboot data-only oracle without old authority>','exec');return raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean current observer required')
    proof=json.loads((W/'pg2806-current-042-before-v1/manifest.safe.json').read_bytes())
    if proof.get('actualExit')!=0 or proof.get('productionSource')!=SOURCE or proof.get('privateBeforeSha256')!=BEFORE:
        raise ValueError('genuine sealed current completed data required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);code=payload().encode()
    (out/'payload.private.py').write_bytes(code)
    with management_gate(P/'current-management-critical.lock'):
        with(out/'observer.private.log').open('xb')as f:
            result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=code,stdout=f,stderr=f,timeout=90)
    value={'actualExit':result.returncode,'source':SOURCE,'payloadSha256':hashlib.sha256(code).hexdigest(),'formalAccepted':False}
    if not result.returncode:value.update(json.loads((out/'observer.private.log').read_bytes()))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return result.returncode


if __name__=='__main__':raise SystemExit(main())
