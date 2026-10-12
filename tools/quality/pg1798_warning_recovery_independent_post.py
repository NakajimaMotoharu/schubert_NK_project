"""Separate current whole seal after limited recovery, not old stop acceptance."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W,P
from pg1674_critical_management_gate import management_gate
from pg1770_next_day_full_warning_seal import payload as previous_payload

SLOT='pg1798-warning-recovery-full-post-v1'


def payload():
    raw=previous_payload()
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SAVE'for t in n.targets)]
    raw=raw.replace(ast.get_source_segment(raw,nodes[-1]),'SAVE=BASE/'+repr(SLOT),1)
    marker=' current=capture();require(current==capture());SAVE.mkdir(mode=0o700)'
    if raw.count(marker)!=1:raise ValueError('one independent whole post boundary required')
    checks="""
 current=capture();require(current==capture())
 baseline=(BASE/'pg1770-next-day-full-warning-seal-v1/before.private.json').read_bytes()
 require(hashlib.sha256(baseline).hexdigest()=='b8ce2d5610f625bd6c2d27be466e843fc09fa239a7f779c8cb4711d718fb8ef9')
 require(current==json.loads(baseline))
 require(not pathlib.Path('/proc/476087').exists()and not pathlib.Path('/proc/476116').exists())
 q="begin read only;select count(*)from pg_stat_activity where datname='schubert_nk'and usename in ('schubert_batch','schubert_migration');select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
 require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()==[b'0',b'0'])
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk',name);s=p.lstat()
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)<8:continue
   d=f[5].split(':');require(len(d)!=3 or (int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
 SAVE.mkdir(mode=0o700)"""
    raw=raw.replace(marker,checks)
    raw=raw.replace("'currentFourOwnedLive':True,","'currentFourOwnedLive':True,'recoveredPairAbsent':True,'managementPeersAdvisoryMA0':True,'allOriginalWholeSnapshotUnchanged':True,")
    from pyflakes.api import check
    if check(raw,'<actual separate recovery full post>'):raise ValueError('closed emitted globals required')
    compile(raw,'<independent recovery whole post>','exec');return raw


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'oldNormalCloseUnknown':True,'formalAccepted':False}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
