"""SSC309 frozen independent red/green; no guest business replay or coverage union."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from pg5540_snapshot_scratch_selected import ROOT,TC,sha,utc,test_names

BASE='0ea400109d79e47327d9fff105ff763f9310a31f'
MODULES=('protocol','storage','bootstrap','api','web','batch')
PACKAGE='dev.codex.schubert.nk.batch.platform.'
CASES={
 'dev.codex.schubert.nk.protocol.codec.PayloadGoldenVectorTest':'protocol',
 'dev.codex.schubert.nk.storage.ResourceScopeTest':'storage',
 'dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest':'bootstrap',
 'dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodecTest':'api',
 'dev.codex.schubert.nk.web.bootstrap.WebProcessLifetimeTest':'web',
 PACKAGE+'RootStartupContextTest':'batch',
 PACKAGE+'MorningServiceReadinessTest':'batch',
 PACKAGE+'MorningServiceReadinessNativeTest':'batch'}
RED={(PACKAGE+'RootStartupContextTest','execgen309001TransientZombieIsPendingGenerationNeverAnExit'),
     (PACKAGE+'MorningServiceReadinessTest','execgen309003PendingGenerationNeedsOrdinaryCommandSocketAndHttp')}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('red','green'));parser.add_argument('--version',default='v1');args=parser.parse_args()
    if not re.fullmatch(r'v[1-9][0-9]*',args.version):raise ValueError('bounded new-only version')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('freeze committed clean input first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    reference=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5588-current3905-cases/qualification.json'
    if sha(reference)!='b34549edfd627c6b4606abbbb9a50eadf47153b37e7b3ad7e3f2aa2a30732878':raise ValueError('original0ea qualification remains fixed')
    before=json.loads(reference.read_bytes())
    if before['productionSource']!=BASE or before['tests']!=3905 or before['mainClasses']!=1664:raise ValueError('actual original whole scope')
    os.umask(0o077);out=ROOT.parent/'pgpt-runs/PG379'/('pg5708-exec-generation-'+args.phase+'-'+args.version);out.mkdir(mode=0o700)
    archive=out/'source.tar'
    with archive.open('xb')as f:
        subprocess.run(['git','archive',head,'src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT,stdout=f,check=True);f.flush();os.fsync(f.fileno())
    snapshot=out/'source';snapshot.mkdir(mode=0o700)
    with tarfile.open(archive)as f:f.extractall(snapshot,filter='data')
    expected={name:test_names(snapshot/('src/schubert-nk-'+module+'/src/test/java')/(name.replace('.','/')+'.java'))for name,module in CASES.items()}
    base=[str(TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-B','-o','-ntp','-Dmaven.repo.local='+str(TC/'m2/repository')]
    modules=','.join('src/schubert-nk-'+m for m in MODULES)
    commands=[base+['-pl',modules,'spotless:check'],base+['-pl',modules,'-Dtest='+','.join(expected),'-Dsurefire.failIfNoSpecifiedTests=false','package','org.jacoco:jacoco-maven-plugin:0.8.15:report','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']]
    inputs={str(p.relative_to(snapshot)):sha(p)for p in snapshot.rglob('*')if p.is_file()}
    env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH')}
    env.update(JAVA_HOME=str(TC/'jdk-25.0.4'),PATH=str(TC/'jdk-25.0.4/bin')+os.pathsep+os.environ['PATH'],MAVEN_OPTS='-Xmx768m -Djava.io.tmpdir='+str(out))
    start=utc();exits=[]
    with(out/'start.safe.json').open('x')as f:json.dump({'sourceSnapshot':head,'startedUTC':start,'commands':commands,'archiveSha256':sha(archive),'replayAllowed':False},f,sort_keys=True)
    for i,command in enumerate(commands,1):
        with(out/f'phase-{i}.private.log').open('xb')as log:
            child=subprocess.Popen(command,cwd=snapshot,env=env,stdout=log,stderr=log,umask=0o027)
            proc=__import__('pathlib').Path('/proc')/str(child.pid)
            with(out/f'phase-{i}.owner.safe.json').open('x')as f:json.dump({'pid':child.pid,'ticks':int((proc/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((proc/'cmdline').read_bytes()).hexdigest()},f,sort_keys=True)
            exits.append(child.wait());log.flush();os.fsync(log.fileno())
        if exits[-1]:break
    actual={};failed=[];errors=[];skipped=[];xmls={};static={};counters={}
    for module in MODULES:
        target=snapshot/('src/schubert-nk-'+module+'/target')
        for path in(target/'surefire-reports').glob('TEST-*.xml'):
            tree=ET.parse(path).getroot();name=tree.get('name')
            if name in actual:raise ValueError('duplicate suite')
            actual[name]=set();xmls[name]=sha(path)
            for case in tree.findall('testcase'):
                method=case.get('name','').removesuffix('()')
                if method in actual[name]:raise ValueError('duplicate named case')
                actual[name].add(method)
                for tag,rows in(('failure',failed),('error',errors),('skipped',skipped)):
                    if case.find(tag)is not None:rows.append([name,method])
                if any(n.tag in('flakyFailure','flakyError','rerunFailure','rerunError')for n in case.iter()):errors.append([name,method,'rerun/flaky'])
        report=target/'spotbugsXml.xml'
        if report.exists():static[module]=len(ET.parse(report).getroot().findall('BugInstance'))
        report=target/'site/jacoco/jacoco.xml'
        if module=='batch'and report.exists():
            counters={c.get('name'):{v.get('type'):{'covered':int(v.get('covered')),'missed':int(v.get('missed'))}for v in c.findall('counter')}for c in ET.parse(report).getroot().findall('package/class')if c.get('name','').endswith(('/RootStartupContext','/MorningServiceReadiness'))}
    physical={m+':'+p.relative_to(snapshot/('src/schubert-nk-'+m+'/target/classes')).as_posix():sha(p)for m in MODULES for p in(snapshot/('src/schubert-nk-'+m+'/target/classes')).rglob('*.class')}
    prior=before['allPhysicalMainSha256'];changes=sorted(k for k in prior if physical.get(k)!=prior[k])
    prefix='batch:dev/codex/schubert/nk/batch/platform/RootStartupContext'
    declared=set(physical)==set(prior)and (not changes if args.phase=='red'else prefix+'.class'in changes and all(k==prefix+'.class'or k.startswith(prefix+'$')for k in changes))
    fixed=all(sha(snapshot/n)==h for n,h in inputs.items())and subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==head and not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
    red=fixed and declared and actual==expected and exits==[0,1]and not errors and not skipped and set(map(tuple,failed))==RED
    green=fixed and declared and actual==expected and exits==[0,0]and not failed and not errors and not skipped and set(static)==set(MODULES)and not any(static.values())
    value={'sourceSnapshot':head,'phase':args.phase,'startedUTC':start,'completedUTC':utc(),'actualExit':next((e for e in exits if e),0),'phaseExits':exits,'sourceFixed':fixed,'exactInventory':actual==expected,'tests':sum(map(len,actual.values())),'suites':len(actual),'failed':failed,'errors':errors,'skipped':skipped,'staticBuiltModules':static,'purposefulRedEstablished':red,'greenSelectedQualified':green,'declaredPhysicalDelta':declared,'physicalDifferences':changes,'allPhysicalMainSha256':physical,'targetCounters':counters,'xmlHashes':xmls,'archiveSha256':sha(archive),'formalAccepted':False,'normalNativeQualified':False,'vmActions':0}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({**{k:v for k,v in value.items()if k not in('allPhysicalMainSha256','targetCounters','xmlHashes','physicalDifferences')},'physicalDifferenceCount':len(changes),'mainClasses':len(physical)},sort_keys=True))
    return 0 if red or green else 1


if __name__=='__main__':raise SystemExit(main())
