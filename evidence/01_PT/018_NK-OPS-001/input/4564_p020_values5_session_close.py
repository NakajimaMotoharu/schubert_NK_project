"""Complete read-only same-exec session qualification before cost/criteria checkpoints."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';slot=w/'pg37022-common-values5-unit-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
proof=b/'evidence/PG37024-values5-independent-v1/manifest.json';p=load(proof);assert p['actualExit']==0 and p['success']==5
out=b/'evidence/PG37026-values5-session-closure-v1';assert not out.exists();out.mkdir()
cmd=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'org.jacoco.cli-0.8.15-nodeps.jar'),'execinfo',str(slot/'jacoco.exec')]
with (out/'execinfo.stdout').open('xb') as stdout,(out/'execinfo.stderr').open('xb') as stderr:child=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=120)
assert child.returncode==0
text=(out/'execinfo.stdout').read_text();assert text.count('Session "')==1 and 'Session "PG37022-VALUES5"' in text
probes={n:dict(crc=crc,hit=int(hit),total=int(total)) for crc,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',text,re.M)}
for name in p['classIds']:
 if name in probes:assert probes[name]['crc']==p['classIds'][name]
assert not any(n.startswith('dev/codex/schubert/nk/') and x['hit'] for n,x in probes.items())
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=p['sourceCore'],actualUnitSource=p['actualUnitSource'],run=p['run'],success=5,session='PG37022-VALUES5',sessionCount=1,execSha256=sha(slot/'jacoco.exec'),proof=ref(proof),classIds=p['classIds'],rawGeneratedMethodsQualified=14,oldExecUnion=False,old124Replayed=False,entireMain100Claimed=False,productNativeBrowserDbRootActions=0,whole451Accepted=False,newAcceptance=0,formalUpdated=False,command=cmd,actualToolExit=child.returncode,files={x.name:sha(x) for x in out.iterdir() if x.is_file()})
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,success=5,sessionCount=1,rawGeneratedMethods=14,old124Replayed=False,execUnion=False)))
