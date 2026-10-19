"""Read only this already-issued host full job; no start/stop, VM, DB or raw-log output."""
import datetime
import json
import os
import shlex
from pg5540_snapshot_scratch_selected import ROOT
from lan_server import run


def main():
    code=r'''
import hashlib,json,os,pathlib,xml.etree.ElementTree as ET
base=pathlib.Path('/home/mini/schubert-nk-pgpt');out=base/'runs/PG5754-six-v1';source=base/'source-full-PG5754'
result={'observedUTC':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'host':os.uname().nodename,'hostBoot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'run':'PG5754-six-v1','vmActions':0,'mutations':0}
begin=out/'begin.safe.json';terminal=out/'manifest.safe.json'
if begin.exists():
 v=json.loads(begin.read_bytes())
 if v.get('productionSource')!='9463db1ac23437043facf95b87f64b9fc7e758bd'or v.get('sourceSnapshotHead')!='9463db1ac23437043facf95b87f64b9fc7e758bd'or v.get('sourceArchiveSha256')!='b94847186cc164d5ded59168516bf93fc1b548add3ccfd7fc89b085899fcd728':raise ValueError('only original fixed source/archive/run')
 result['begin']={k:v[k]for k in('run','startUTC','pid','ticks','productionSource','sourceSnapshotHead','workers','sourceArchiveSha256')};result['beginSha256']=hashlib.sha256(begin.read_bytes()).hexdigest()
 proc=pathlib.Path('/proc')/str(v['pid']);matched=False
 try:
  stat=(proc/'stat').read_text().rsplit(')',1)[1].split();argv=(proc/'cmdline').read_bytes().split(bytes([0]));matched=int(stat[19])==v['ticks']and argv[-2:]==[b'/home/mini/schubert-nk-pgpt/tools/pg5754-full.py',b'']and(proc/'status').stat().st_uid==os.getuid()
 except(FileNotFoundError,ProcessLookupError):pass
 result['parentIdentityMatched']=matched;result['state']='ORIGINAL_PARENT_RUNNING'if matched else'PARENT_NOT_VERIFIED'
else:result['state']='BEGIN_NOT_YET_OBSERVED'
modules={};unstable=0
for m in('protocol','storage','bootstrap','api','web','batch'):
 counts={'observedXml':0,'observedTests':0,'observedFailures':0,'observedErrors':0,'observedSkipped':0}
 for p in(source/('src/schubert-nk-'+m+'/target/surefire-reports')).glob('TEST-*.xml'):
  try:
   before=p.stat();raw=p.read_bytes();after=p.stat()
   if(before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):unstable+=1;continue
   root=ET.fromstring(raw);counts['observedXml']+=1
   for k in('Tests','Failures','Errors','Skipped'):counts['observed'+k]+=int(root.get(k.lower(),'0'))
  except(ET.ParseError,FileNotFoundError):unstable+=1
 modules[m]=counts
result.update(modules=modules,unstableObservations=unstable,partialResultsAreNotAcceptance=True)
if terminal.exists():
 t=json.loads(terminal.read_bytes())
 if t.get('productionSource')!='9463db1ac23437043facf95b87f64b9fc7e758bd'or t.get('run')!='PG5754-six-v1':raise ValueError('original terminal identity')
 result['terminal']={k:t[k]for k in('run','actualExit','mavenExit','sourceInputsUnchanged','productionSource','tests','startUTC','endUTC','issues')};result['terminalSha256']=hashlib.sha256(terminal.read_bytes()).hexdigest();result['state']='ORIGINAL_TERMINAL_RECORDED'
print(json.dumps(result,sort_keys=True))
'''
    status,output=run('python3 -B -c '+shlex.quote(code),timeout=40)
    if status:raise ValueError('original job observation failed; never restart')
    v=json.loads(next(line for line in reversed(output.splitlines())if line.startswith('{')))
    out=ROOT.parent/'pgpt-runs/PG379/pg5754-private-contract-six-v1/observations';os.umask(0o077);out.mkdir(exist_ok=True)
    name=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.safe.json'
    with(out/name).open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(v,sort_keys=True))


if __name__=='__main__':main()
