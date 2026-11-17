"""Capture formatter outputs before validation and preserve every Java lexical token."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from public_catch_manual_lexer import lexical
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=b/'evidence/PG37210-monitor-lock4-source-v1/manifest.json';p=json.loads(sp.read_text());paths=[x['path'] for x in p['mainChanges']]+['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/MonitoringLockContractTest.java']
out=b/'evidence/PG37212-monitor-lock4-format-v1';assert not out.exists();out.mkdir();rows=[]
for n in paths:
 src=r/n;raw=src.read_bytes();name=src.name
 command=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--assume-filename',name,'-']
 result=subprocess.run(command,input=raw,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
 (out/(name+'.stdout')).write_bytes(result.stdout);(out/(name+'.stderr')).write_bytes(result.stderr)
 assert result.returncode==0
 assert [t for t,_ in lexical(raw.decode())]==[t for t,_ in lexical(result.stdout.decode())]
 src.write_bytes(result.stdout);rows.append(dict(path=n,beforeFormatSha256=hashlib.sha256(raw).hexdigest(),afterFormatSha256=sha(src),actualExit=result.returncode,command=command,literalsAndAllTokensExact=True))
assert all(sha(r/n)==h for n,h in p['originalTestSourceHashes'].items())
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourcePatch=dict(path=str(sp.relative_to(r)),sha256=sha(sp)),files=rows,original42TestSourcesUnchanged=True,newTests=6,productTestsExecuted=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,formatted=len(rows),newTests=6,productTests=0)))
