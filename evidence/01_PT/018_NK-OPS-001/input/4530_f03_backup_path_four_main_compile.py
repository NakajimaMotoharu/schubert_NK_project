"""Compile the frozen SSC450 Main source with original POMs; no product Test or app execution."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain'
core=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
work=r.parent/'pgpt-runs/PG379/pg36956-backup-path-four-main-compile-v1'
out=b/'evidence/PG36956-backup-path-four-main-compile-v1'
assert not work.exists() and not out.exists()
start=json.loads((r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/044_F03固定Path是正群開始.json').read_text())
assert start['values']['groupCapPp']==5 and start['values']['sameExistingUnfinishedPriceNotAdditional']
equiv=json.loads((b/'evidence/PG36870-ssc450-sql-equivalence-v1/manifest.json').read_text())
assert equiv['actualExit']==0 and equiv['originalTestSourcesUnchanged']
modules=['protocol','storage','bootstrap','batch'];all_modules=['protocol','storage','bootstrap','api','web','batch']
paths=['pom.xml','program/characterization/pom.xml']+['src/schubert-nk-'+m+'/pom.xml' for m in all_modules]
main=sorted(p for module in modules for p in (r/('src/schubert-nk-'+module)/'src/main/java').rglob('*.java'))
assert len(main)==477;paths.extend(str(p.relative_to(r)) for p in main)
assert not any(any(name in p for name in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest','SnapshotKeyCloseWitness','pg9892_snapshot']) for p in paths)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
work.mkdir();out.mkdir();snapshot=work/'snapshot';snapshot.mkdir();pins={}
for name in paths:
    raw=(r/name).read_bytes();assert subprocess.check_output(['git','show',core+':'+name])==raw
    target=snapshot/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);pins[name]=sha(r/name)
command=[str(tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','-B','-ntp',
    '-Dmaven.repo.local='+str(tc/'m2/repository'),'-pl',','.join('src/schubert-nk-'+m for m in modules),'-am','compile']
env={'PATH':str(tc/'jdk-25.0.4/bin')+':/usr/bin:/bin','JAVA_HOME':str(tc/'jdk-25.0.4'),'HOME':os.environ['HOME'],'LANG':'C.UTF-8'}
begin=dict(sourceCore=core,groupId=start['groupId'],groupStartEvent=start['eventId'],mainCount=477,inputHashes=pins,
    cwd=str(snapshot),command=command,startAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    noTestSources=True,canonicalCostOwner='WBS-F03',notAdditionalOriginalF03Charge=True)
(out/'begin.safe.json').open('x').write(json.dumps(begin,indent=2)+'\n')
with (out/'maven.stdout.log').open('xb') as stdout,(out/'maven.stderr.log').open('xb') as stderr:
    try:
        process=subprocess.run(command,cwd=snapshot,env=env,stdout=stdout,stderr=stderr,timeout=180)
        exit_code=process.returncode;timed_out=False
    except subprocess.TimeoutExpired:exit_code=124;timed_out=True
classes={module:{str(p.relative_to(snapshot/('src/schubert-nk-'+module)/'target/classes')):sha(p)
    for p in sorted((snapshot/('src/schubert-nk-'+module)/'target/classes').rglob('*.class'))} for module in modules}
assert all(sha(r/p)==h==sha(snapshot/p) for p,h in pins.items())
assert not list(snapshot.rglob('surefire-reports'))
result=dict(begin,actualExit=exit_code,timedOut=timed_out,physicalClassHashes=classes,
    terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productTestsExecuted=0,
    logs={name:sha(out/name) for name in ['maven.stdout.log','maven.stderr.log']},
    actualNativeDbVmServiceActions=0,heldClassfileActions=0,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(actualExit=exit_code,sourceCore=core,physical={k:len(v) for k,v in classes.items()},productTestsExecuted=0)))
raise SystemExit(exit_code)
