"""Authenticate immutable actual admission original and independent day15 selectors only."""
import datetime
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg2862_network_newcurrent_observer import SOURCE
from pg478_cleanup_oracle import instant,older,candidates
from pg1766_next_day_independent_candidates import classify_inbox

SLOT='pg2876-network-admission-original-v1'


def payload():
    live=json.loads((W/'pg2874-network-newcurrent-live-binding-v1/manifest.safe.json').read_bytes())
    if live.get('actualExit')!=0 or live.get('productionSource')!=SOURCE:raise ValueError('actual same new run binding required')
    binding=live['binding']
    raw='import datetime,hashlib,json,os,pathlib,stat\n'+''.join(inspect.getsource(f)+'\n'for f in [instant,older,candidates,classify_inbox])
    raw+='BINDING='+repr(binding)+'\n'+BODY
    from pyflakes.api import check
    if check(raw,'<immutable original and independent day selectors>'):raise ValueError('complete immutable original oracle namespace required')
    compile(raw,'<before selectors, no actual DB oracle>','exec');return raw


BODY=r'''
require=lambda v:None if v else (_ for _ in ()).throw(ValueError('actual immutable new admission original refused'))
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-','')==BINDING['boot'])
p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg2872-network-newcurrent-noargs-once-v2/external-before.private.json')
def metadata(p):
 s=p.lstat();return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
m=metadata(p);require(m[2:6]==[0,0,stat.S_IFREG|0o600,1]and not os.listxattr(p))
fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:raw=os.pread(fd,m[6]+1,0);require(len(raw)==m[6])
finally:os.close(fd)
require(metadata(p)==m and p.read_bytes()==raw and metadata(p)==m)
before=json.loads(raw);require(set(before)=={'immutable','runtime','trees','observer'})
immutable=before['immutable'];require(immutable['boot']=='79a3260a-e16d-42bf-942a-b914ed144c28'and immutable['source']=='04207efc3ad78bca75942153a90c70985064c988'and len(immutable['rows'])==24)
day=instant(BINDING['cutoff']).astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
require(day=='2026-10-15')
require(not any(row['business_date']==day for row in immutable['rows']['schubert.batch_runs']))
expected=candidates(immutable['rows'],BINDING['cutoff']);inbox=classify_inbox(immutable['rows'],expected['inbox_scan_candidates'])
out=pathlib.Path('/var/lib/pgpt-s1-preservation/pg2876-network-admission-original-v1');os.umask(0o077);out.mkdir(mode=0o700)
oracle={'beforeSha256':hashlib.sha256(raw).hexdigest(),'cutoff':BINDING['cutoff'],'day':day,'expected':expected,'expectedInbox':inbox}
encoded=json.dumps(oracle,sort_keys=True).encode()
with(out/'oracle.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'source':'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25','immutableRetainedSource':immutable['source'],
 'privateBeforeSha256':hashlib.sha256(raw).hexdigest(),'oracleSha256':hashlib.sha256(encoded).hexdigest(),'tables':24,
 'businessDay':day,'currentDayNoPriorHistory':True,'candidateCounts':{k:len(v)for k,v in expected.items()},
 'expectedInboxDeleted':len(inbox['deleted']),'expectedInboxProtected':len(inbox['protected']),
 'actualDbRowsRead':0,'productionCalls':0,'startsStopsSqlWrites0':True,'rawExported':False,'formalAccepted':False}))
'''


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed original capture required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode()
    with(out/'payload.private.py').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        with(out/'observer.private.log').open('xb')as f:r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,stdout=f,stderr=f,timeout=30);f.flush();os.fsync(f.fileno())
    value={'actualExit':r.returncode,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw).hexdigest(),'startedUTC':started,
        'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:value['guest']=json.loads((out/'observer.private.log').read_bytes())
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
