"""Bounded actor/destination facts only; no credential reads, locks, DB, signals or VM actions."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W,P
from pg1674_critical_management_gate import management_gate

BODY=r'''
import hashlib,json,os,pathlib,stat
P=pathlib.Path
assert P('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'
assert P('/opt/schubert-nk/current').resolve(strict=True)==P('/opt/schubert-nk/releases/0.1.0-PG3976')
raw=P('/var/lib/pgpt-s1-preservation/pg4080-failed-ordinary-full-capture-v1/observed.private.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='fd1177d10f2713596a32de536a3c71d592563cc3b6decb7194bc6c68ea6c21d8'
old=json.loads(raw);result={}
for unit in ['schubert-nk-api.service','schubert-nk-web.service']:
 actor=old['second']['actors'][unit];p=P('/proc')/str(actor['pid']);cmd=(p/'cmdline').read_bytes()
 assert hashlib.sha256(cmd).hexdigest()==actor['argvSha256']and int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==actor['ticks']
 agents=[a for a in cmd.split(b'\0')if a.startswith(b'-javaagent:')];assert len(agents)==1
 options=agents[0].split(b'=',1)[1].decode('ascii').split(',');dest=[o.removeprefix('destfile=')for o in options if o.startswith('destfile=')];assert len(dest)==1
 path=P(dest[0]);assert path.is_absolute()and '..'not in path.parts
 s=path.parent.lstat();result[unit]={'destUnderFixedNativeRoot':path.is_relative_to(P('/run/schubert-nk/pt-coverage')),'destExists':os.path.lexists(path),
 'parentIsDirectory':stat.S_ISDIR(s.st_mode),'parentMode':stat.S_IMODE(s.st_mode),'parentUid':s.st_uid,'parentGid':s.st_gid,
 'actorUid':int((p/'status').read_text().split('Uid:',1)[1].splitlines()[0].split()[0]),
 'dumpOnExitTrue':'dumponexit=true'in options,'appendTrue':'append=true'in options,'destinationSha256':hashlib.sha256(str(path).encode()).hexdigest()}
 assert(p/'cmdline').read_bytes()==cmd
print(json.dumps({'actualExit':0,'source':old['source'],'BOM':old['BOM'],'destinations':result,'stateChangingActions':0}))
'''


def main():
    os.umask(0o077);out=W/'pg4120-native-destination-read-v1';out.mkdir()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=BODY.encode(),capture_output=True,timeout=30)
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','payloadSha256':hashlib.sha256(BODY.encode()).hexdigest()}
    if r.returncode==0:value['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
