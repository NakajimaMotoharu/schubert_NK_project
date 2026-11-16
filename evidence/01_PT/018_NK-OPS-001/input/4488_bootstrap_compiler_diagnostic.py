"""BUG3129 bounded Main-only diagnostic; no secret settings, tests or app execution."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

r=Path.cwd();tc=r.parent/'toolchain';b=r/'evidence/01_PT/018_NK-OPS-001/evidence'
previous=b/'PG36830-four-main-compile-v1/manifest.json';m=json.loads(previous.read_text())
assert m['actualExit']==1 and not m['physicalClassHashes']['bootstrap']
assert '## BUG-3129 ' in (r/'documents/900_OTHER/910_台帳/915_障害表.md').read_text()
work=r.parent/'pgpt-runs/PG379/pg36834-bootstrap-compiler-diagnostic-v1'
out=b/'PG36834-bootstrap-compiler-diagnostic-v1'
assert not work.exists() and not out.exists();work.mkdir();out.mkdir()
snapshot=work/'snapshot';snapshot.mkdir();home=work/'tool-home';home.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
for name,h in m['inputHashes'].items():
    if not (name.endswith('/pom.xml') or name=='pom.xml' or
            name.startswith(('src/schubert-nk-bootstrap/src/main/java/',
                             'src/schubert-nk-storage/src/main/java/'))):continue
    assert sha(r/name)==h
    raw=(r/name).read_bytes();p=snapshot/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(raw);pins[name]=h
assert len([p for p in pins if p.endswith('.java')])==112
assert not list(snapshot.rglob('*.class'))
settings=work/'empty-settings.xml'
settings.write_text('<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0"/>\n')
command=[str(tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),
 '-o','-B','-ntp','-X','-s',str(settings),'-gs',str(settings),
 '-Dmaven.repo.local='+str(tc/'m2/repository'),'-Dmaven.compiler.verbose=true',
 '-pl','src/schubert-nk-bootstrap','-am','compile']
env={'PATH':str(tc/'jdk-25.0.4/bin')+':/usr/bin:/bin',
 'JAVA_HOME':str(tc/'jdk-25.0.4'),'HOME':str(home),'LANG':'C.UTF-8',
 'MAVEN_OPTS':'-Duser.home='+str(home)}
begin=dict(sourceCore=m['sourceCore'],originalFailureSha256=sha(previous),
 originalFailure='PG36830',bug='BUG3129',horizontal='YKT2600',inputHashes=pins,
 command=command,controlledEnvironmentKeys=sorted(env),settingsEmpty=True,
 startAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
(out/'begin.safe.json').open('x').write(json.dumps(begin,indent=2)+'\n')
with (work/'compiler.stdout.log').open('xb') as stdout,(work/'compiler.stderr.log').open('xb') as stderr:
    try:
        result=subprocess.run(command,cwd=snapshot,env=env,stdout=stdout,stderr=stderr,timeout=180)
        exit_code=result.returncode;timeout=False
    except subprocess.TimeoutExpired:exit_code=124;timeout=True
assert all(sha(r/p)==h==sha(snapshot/p) for p,h in pins.items())
assert not list(snapshot.rglob('surefire-reports'))
result=dict(begin,actualExit=exit_code,timedOut=timeout,
 terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 logs={name:dict(path=str(work/name),sha256=sha(work/name))
       for name in ['compiler.stdout.log','compiler.stderr.log']},
 diagnosticOnly=True,qualityQualified=False,productTestsExecuted=0,
 actualNativeDbVmServiceActions=0,heldClassfileActions=0,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(actualExit=exit_code,timedOut=timeout,diagnosticOnly=True,originalFailure='PG36830')))
