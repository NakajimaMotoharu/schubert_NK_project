"""Isolated first server selected PT; no historical result or formal credit."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

BASE = Path('/home/mini/schubert-nk-pgpt')
OUT = BASE/'runs/PG1430-selected-v1'
SOURCE = BASE/'source'
MODULES = ['protocol','storage','bootstrap','batch']
SUITES = {'MorningServiceReadinessTest':7,'ArtemisRoleReadinessClientTest':4,
          'MorningBackupRetentionTest':10,'MorningBackupRequestPublicationTest':7}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    OUT.mkdir(mode=0o700)
    (OUT/'tmp').mkdir(mode=0o700)
    assert os.statvfs(BASE).f_bavail*os.statvfs(BASE).f_frsize > 125*1024**3
    # Newly extracted source, not shared targets or old host XML.
    assert not any((SOURCE/f'src/schubert-nk-{m}/target').exists() for m in MODULES)
    env={**os.environ,'JAVA_HOME':str(BASE/'tools/jdk-25.0.4'),
         'PATH':str(BASE/'tools/jdk-25.0.4/bin')+':'+os.environ['PATH'],
         'MAVEN_OPTS':'-Xmx768m','JAVA_TOOL_OPTIONS':'-Djava.io.tmpdir='+str(OUT/'tmp')}
    args=[str(BASE/'tools/maven/bin/mvn'),'-o','--no-transfer-progress','-Dstyle.color=never',
          '-Djansi.force=false','-Dmaven.repo.local='+str(BASE/'m2/repository')]
    dependency=args+['-pl',','.join('src/schubert-nk-'+m for m in MODULES[:3]),
                     'spotless:check','test-compile','jar:test-jar','jar:jar','install:install']
    selected=args+['-pl','src/schubert-nk-batch','-Dtest='+','.join(SUITES),
                   'spotless:check','test-compile','test','spotbugs:check','jacoco:report','jar:jar']
    start=datetime.datetime.now(datetime.timezone.utc)
    with (OUT/'start.safe.json').open('x') as f:
        json.dump({'startUTC':start.isoformat(),'sourceSnapshotHead':'2c29d7a17a5eca2f61b24e99af13260a3c286a09',
            'productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','dependencyCommand':dependency,
            'selectedCommand':selected,'requiredSelected':28,'workers':1,'formalAccepted':False},f)
    with (OUT/'maven.private.log').open('xb') as f:
        dep=subprocess.run(dependency,cwd=SOURCE,env=env,stdout=f,stderr=subprocess.STDOUT)
        result=subprocess.run(selected,cwd=SOURCE,env=env,stdout=f,stderr=subprocess.STDOUT) if dep.returncode==0 else None
        f.flush();os.fsync(f.fileno())
    reports=SOURCE/'src/schubert-nk-batch/target/surefire-reports'
    counts={};missing=[]
    for name, expected in SUITES.items():
        paths=list(reports.glob('TEST-*.'+name+'.xml'))
        if len(paths)!=1 or paths[0].stat().st_mtime_ns < int(start.timestamp()*1e9):
            missing.append(name);continue
        root=ET.parse(paths[0]).getroot()
        value={k:int(root.attrib[k]) for k in ['tests','failures','errors','skipped']}
        if value!={'tests':expected,'failures':0,'errors':0,'skipped':0}:
            missing.append(name)
        counts[name]={**value,'xmlSha256':sha(paths[0])}
    spot=SOURCE/'src/schubert-nk-batch/target/spotbugsXml.xml'
    static=len(ET.parse(spot).getroot().findall('BugInstance')) if spot.exists() else None
    passed=dep.returncode==0 and result is not None and result.returncode==0 and not missing and static==0
    manifest={'run':'PG1430-selected-v1','dependencyExit':dep.returncode,'selectedExit':result.returncode if result else None,
        'counts':counts,'missingOrNonpassing':missing,'staticIssues':static,'actualExit':0 if passed else 1,
        'sourceSnapshotHead':'2c29d7a17a5eca2f61b24e99af13260a3c286a09','startUTC':start.isoformat(),
        'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False,
        'wholeRegressionNotRun':True,'selectedPtNewProductionCredit':0,
        'failureLogSha256':sha(OUT/'maven.private.log'),'coverageExecSha256':sha(SOURCE/'src/schubert-nk-batch/target/jacoco.exec') if (SOURCE/'src/schubert-nk-batch/target/jacoco.exec').exists() else None}
    with (OUT/'manifest.safe.json').open('x') as f:
        json.dump(manifest,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(manifest))
    return 0 if passed else 1


if __name__=='__main__':
    raise SystemExit(main())
