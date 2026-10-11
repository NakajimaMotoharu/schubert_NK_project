"""Fresh isolated static/auth cause tests; preserve failure and private DB logs."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

BASE = Path('/home/mini/schubert-nk-pgpt')
OUT = BASE/'runs/PG1466-selected-v1'
SOURCE = BASE/'source-selected-PG1466'
SUITES = ['InspectorDeploymentTest','ApplicationServiceUnitTest','AuthenticationServiceTest']


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    os.umask(0o077);OUT.mkdir(mode=0o700);(OUT/'tmp').mkdir(mode=0o700)
    assert os.statvfs(BASE).f_bavail*os.statvfs(BASE).f_frsize>=10*1024**3
    assert not (SOURCE/'src/schubert-nk-api/target').exists()
    inputs={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file()}
    env={**os.environ,'JAVA_HOME':str(BASE/'tools/jdk-25.0.4'),
         'PATH':str(BASE/'tools/jdk-25.0.4/bin')+':'+os.environ['PATH'],
         'MAVEN_OPTS':'-Xmx768m -Djava.io.tmpdir='+str(OUT/'tmp'),
         'SCHUBERT_PG_ROOT':str(BASE/'tools/postgresql18/usr'),
         'SCHUBERT_AUTH_DIAGNOSTICS':'true',
         'SCHUBERT_SHELLCHECK':str(BASE/'tools/shellcheck-0.11.0')}
    env.pop('JAVA_TOOL_OPTIONS',None)
    args=[str(BASE/'tools/maven/bin/mvn'),'-o','--no-transfer-progress','-Dstyle.color=never',
          '-Djansi.force=false','-Djava.io.tmpdir='+str(OUT/'tmp'),
          '-Dmaven.repo.local='+str(BASE/'m2/repository'),'-pl','src/schubert-nk-api',
          '-Dtest='+','.join(SUITES),'spotless:check','test-compile','test',
          'spotbugs:check','jacoco:report','jar:jar']
    start=datetime.datetime.now(datetime.timezone.utc)
    with (OUT/'begin.safe.json').open('x') as f:
        json.dump({'startUTC':start.isoformat(),'pid':os.getpid(),
           'ticks':int(Path('/proc/self/stat').read_text().rpartition(')')[2].split()[19]),
           'inputs':inputs,'command':args,'productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f',
           'expectedSuites':SUITES,'formalAccepted':False},f,sort_keys=True);f.flush();os.fsync(f.fileno())
    with (OUT/'maven.private.log').open('xb') as f:
        r=subprocess.run(args,cwd=SOURCE,env=env,stdout=f,stderr=subprocess.STDOUT,umask=0o027)
        f.flush();os.fsync(f.fileno())
    results={}
    for p in (SOURCE/'src/schubert-nk-api/target/surefire-reports').glob('TEST-*.xml'):
        x=ET.parse(p).getroot()
        results[x.attrib['name']]={k:int(x.attrib[k]) for k in ['tests','failures','errors','skipped']}
        results[x.attrib['name']]['xmlSha256']=sha(p)
    # Private log statements may contain synthetic passwords/SQL parameters.
    # Only counts of known diagnostic categories cross the evidence boundary.
    categories={}
    for p in list((OUT/'tmp').rglob('postgresql.log'))+list((OUT/'tmp').glob('auth-diagnostic-*.private.log')):
        text=p.read_text(errors='replace')
        for category in ['canceling statement due to lock timeout',
                         'canceling statement due to statement timeout', 'deadlock detected']:
            categories[category]=categories.get(category,0)+text.count(category)
    end=datetime.datetime.now(datetime.timezone.utc)
    result={'run':'PG1466-selected-v1','mavenExit':r.returncode,
            'sourceInputsUnchanged':all(sha(SOURCE/p)==h for p,h in inputs.items()),
            'startUTC':start.isoformat(),'endUTC':end.isoformat(),
            'elapsedSeconds':(end-start).total_seconds(),'suites':results,
            'databaseDiagnosticCounts':categories,'logSha256':sha(OUT/'maven.private.log'),
            'formalAccepted':False,'wholeRegressionAccepted':False}
    with (OUT/'manifest.safe.json').open('x') as f:
        json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result,sort_keys=True))
    return r.returncode


if __name__=='__main__':raise SystemExit(main())
