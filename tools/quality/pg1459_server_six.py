"""Isolated sameMain/testSnapshot fresh six on LAN, worker1, no VM mutation."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

BASE=Path('/home/mini/schubert-nk-pgpt')
OUT=BASE/'runs/PG1459-six-v1'
SOURCE=BASE/'source-full-PG1459'
MODULES=['protocol','storage','bootstrap','api','web','batch']
ARCHIVE_SHA='f12e38a72f25fc233a42d3eff05e660d708bde9716a31d3c3f255fada824a3a1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def complete_result(exit_code,same,issues,tests,suites,classes):
    return (type(exit_code)is int and exit_code==0 and same is True
            and type(issues)is list and not issues
            and type(tests)is int and tests==3576
            and type(suites)is int and suites==523
            and type(classes)is int and classes==1635)


def main():
    os.umask(0o077);OUT.mkdir(mode=0o700);(OUT/'tmp').mkdir(mode=0o700)
    assert os.statvfs(BASE).f_bavail*os.statvfs(BASE).f_frsize>=10*1024**3
    assert SOURCE.is_dir()and not any((SOURCE/f'src/schubert-nk-{m}/target').exists()for m in MODULES)
    assert sha(BASE/'transfer/source.tar')==ARCHIVE_SHA
    inputs={str(p.relative_to(SOURCE)):sha(p)for p in SOURCE.rglob('*')if p.is_file()}
    assert inputs
    env={**os.environ,'JAVA_HOME':str(BASE/'tools/jdk-25.0.4'),'PATH':str(BASE/'tools/jdk-25.0.4/bin')+':'+os.environ['PATH'],'MAVEN_OPTS':'-Xmx768m -Djava.io.tmpdir='+str(OUT/'tmp'),'SCHUBERT_PG_ROOT':str(BASE/'tools/postgresql18/usr')}
    env.pop('JAVA_TOOL_OPTIONS',None)
    args=[str(BASE/'tools/maven/bin/mvn'),'-o','--no-transfer-progress','-Dstyle.color=never','-Djansi.force=false','-Djava.io.tmpdir='+str(OUT/'tmp'),'-Dmaven.repo.local='+str(BASE/'m2/repository'),'-Dnk.pt.node='+str(BASE/'tools/node-v24.19.0/bin/node'),'-pl',','.join('src/schubert-nk-'+m for m in MODULES),'clean','spotless:check','test-compile','jar:test-jar','test','spotbugs:check','jacoco:report','jar:jar']
    start=datetime.datetime.now(datetime.timezone.utc)
    begin={'run':'PG1459-six-v1','startUTC':start.isoformat(),'pid':os.getpid(),'ticks':int(Path('/proc/self/stat').read_text().rpartition(')')[2].split()[19]),'sourceSnapshotHead':'2c29d7a17a5eca2f61b24e99af13260a3c286a09','productionSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','command':args,'workers':1,'formalAccepted':False,'sourceArchiveSha256':ARCHIVE_SHA,'inputs':inputs}
    with(OUT/'begin.safe.json').open('x')as f:json.dump(begin,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    with(OUT/'maven.private.log').open('xb')as f:
        r=subprocess.run(args,cwd=SOURCE,env=env,stdout=f,stderr=subprocess.STDOUT,umask=0o027);f.flush();os.fsync(f.fileno())
    end=datetime.datetime.now(datetime.timezone.utc);same=all(sha(SOURCE/p)==h for p,h in inputs.items())
    modules={};total=0;issues=[];classes={};end_ns=int(end.timestamp()*1e9);start_ns=int(start.timestamp()*1e9)
    for m in MODULES:
        root=SOURCE/f'src/schubert-nk-{m}/target';save=OUT/m;save.mkdir(mode=0o700)
        reports=list((root/'surefire-reports').glob('TEST-*.xml'));count={k:0 for k in['tests','failures','errors','skipped']};xmls={};flaky=0
        for p in reports:
            t=ET.parse(p).getroot();cases=t.findall('testcase')
            if not start_ns<=p.stat().st_mtime_ns<=end_ns or len(cases)!=int(t.attrib['tests']):issues.append(m+':xmlTimeOrCount')
            for k in count:count[k]+=int(t.attrib[k])
            for c in cases:
                if any(c.find(k)is not None for k in['flakyFailure','flakyError','rerunFailure','rerunError']):flaky+=1
            xmls[p.name]=sha(p)
        spot=root/'spotbugsXml.xml';static=len(ET.parse(spot).getroot().findall('.//BugInstance'))if spot.exists()else None
        coverage=root/'site/jacoco/jacoco.xml';counters={};sessions=[]
        if coverage.exists():
            t=ET.parse(coverage).getroot();counters={c.attrib['type']:{'missed':int(c.attrib['missed']),'covered':int(c.attrib['covered'])}for c in t.findall('counter')};sessions=[dict(n.attrib)for n in t.findall('sessioninfo')]
        jar=root/f'schubert-nk-{m}-0.1.0-SNAPSHOT.jar';compiled={}
        if jar.exists():
            with zipfile.ZipFile(jar)as z:compiled={n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
        for path in [root/'surefire-reports',spot,coverage,root/'jacoco.exec',jar]:
            if path.is_dir():shutil.copytree(path,save/path.name)
            elif path.is_file():shutil.copy2(path,save/path.name)
        value={**count,'suites':len(reports),'flaky':flaky,'staticIssues':static,'coverage':counters,'sessions':sessions,'xmlHashes':xmls,'mainClasses':len(compiled),'mainClassHashes':compiled}
        modules[m]=value;total+=count['tests'];classes[m]=compiled
        if not reports or count['failures']or count['errors']or count['skipped']or flaky or static!=0 or not counters or not sessions or not compiled:issues.append(m+':incompleteOrNonpassing')
    passed=complete_result(r.returncode,same,issues,total,sum(v['suites']for v in modules.values()),sum(v['mainClasses']for v in modules.values()))
    result={'run':'PG1459-six-v1','actualExit':0 if passed else 1,'mavenExit':r.returncode,'sourceInputsUnchanged':same,'sourceSnapshotHead':begin['sourceSnapshotHead'],'productionSource':begin['productionSource'],'startUTC':start.isoformat(),'endUTC':end.isoformat(),'elapsedSeconds':(end-start).total_seconds(),'tests':total,'expectedTests':3576,'modules':modules,'issues':issues,'logSha256':sha(OUT/'maven.private.log'),'mainClassByteEqualityToVmPending':True,'sameSourceNativeCampaignPending':True,'formalAccepted':False}
    with(OUT/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in result.items()if k!='modules'},sort_keys=True));return result['actualExit']


if __name__=='__main__':raise SystemExit(main())
