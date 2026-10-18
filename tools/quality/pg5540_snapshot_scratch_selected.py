"""Frozen local red/green scratch fault selection; no VM or previous success import."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
TC=ROOT.parent/'toolchain'
BASE='29612b2a484a5ab7418e02a491c4360af7444626'
BUILT=('protocol','storage','bootstrap','api')
PACKAGE='dev.codex.schubert.nk.api.idempotency.'
FAULT={
    'scratch001CompressAllocationFailureCannotOwnNativeDeflater',
    'scratch002DecompressAllocationFailureCannotOwnNativeInflater',
    'scratch003NegativeControlDetectsDeflaterBeforeUnprotectedArray',
    'scratch004NegativeControlDetectsInflaterBeforeUnprotectedArray'}
DEPENDENCIES={
    'dev.codex.schubert.nk.protocol.codec.PayloadGoldenVectorTest':('protocol',3),
    'dev.codex.schubert.nk.storage.ResourceScopeTest':('storage',8),
    'dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest':('bootstrap',7)}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()


def test_names(path):
    raw=path.read_text()
    if any(n in raw for n in('@Disabled','@ParameterizedTest','@RepeatedTest','@TestFactory')):
        raise ValueError('explicit nonparameterized unskipped selected inventory only')
    names=re.findall(r'@Test\s+(?:public\s+)?void\s+(\w+)\s*\(\s*\)',raw)
    if len(names)!=raw.count('@Test')or len(set(names))!=len(names):raise ValueError('one named case per selected Test annotation')
    return set(names)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('red','green'));parser.add_argument('--version',default='v1')
    args=parser.parse_args()
    if not re.fullmatch(r'v[1-9][0-9]*',args.version):raise ValueError('new-only bounded version')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed scratch source required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    os.umask(0o077);out=ROOT.parent/'pgpt-runs/PG379'/('pg5540-snapshot-scratch-'+args.phase+'-'+args.version);out.mkdir(mode=0o700)
    archive=out/'source.tar'
    with archive.open('xb')as target:
        subprocess.run(['git','archive',head,'src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT,stdout=target,check=True)
        target.flush();os.fsync(target.fileno())
    snapshot=out/'source';snapshot.mkdir(mode=0o700)
    with tarfile.open(archive)as source:source.extractall(snapshot,filter='data')
    tests=snapshot/'src/schubert-nk-api/src/test/java'/PACKAGE.replace('.','/')
    expected={PACKAGE+'SnapshotScratchOwnershipTest':FAULT}
    if test_names(tests/'SnapshotScratchOwnershipTest.java')!=FAULT:raise ValueError('four independent fixed fault cases')
    for name,(module,count)in DEPENDENCIES.items():
        path=snapshot/('src/schubert-nk-'+module+'/src/test/java')/(name.replace('.','/')+'.java')
        names=test_names(path)
        if len(names)!=count:raise ValueError('explicit unchanged dependency contract inventory')
        expected[name]=names
    if args.phase=='green':
        names=test_names(tests/'ResponseSnapshotCodecTest.java')
        if len(names)!=7:raise ValueError('all original seven independent codec vectors required')
        expected[PACKAGE+'ResponseSnapshotCodecTest']=names
    base=[str(TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-B','-o','-ntp','-Dmaven.repo.local='+str(TC/'m2/repository')]
    commands=[base+['-pl',','.join('src/schubert-nk-'+m for m in('protocol','storage','bootstrap','api','web','batch')),'spotless:check'],
        base+['-pl','src/schubert-nk-api','-am','-Dtest='+','.join(expected),'-Dsurefire.failIfNoSpecifiedTests=false','package',
            'org.jacoco:jacoco-maven-plugin:0.8.15:report','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']]
    inputs={str(p.relative_to(snapshot)):sha(p)for p in snapshot.rglob('*')if p.is_file()}
    env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH')}
    env.update(JAVA_HOME=str(TC/'jdk-25.0.4'),PATH=str(TC/'jdk-25.0.4/bin')+os.pathsep+os.environ['PATH'],MAVEN_OPTS='-Xmx768m -Djava.io.tmpdir='+str(out))
    started=utc();phases=[]
    (out/'start.safe.json').write_text(json.dumps({'sourceSnapshot':head,'baseProductionSource':BASE,'phase':args.phase,'startedUTC':started,'commands':commands,'archiveSha256':sha(archive),'replayAllowed':False},sort_keys=True))
    for index,command in enumerate(commands,1):
        with(out/f'phase-{index}.private.log').open('xb')as log:
            child=subprocess.Popen(command,cwd=snapshot,env=env,stdout=log,stderr=log,umask=0o027)
            proc=Path('/proc')/str(child.pid)
            owner={'pid':child.pid,'ticks':int((proc/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((proc/'cmdline').read_bytes()).hexdigest()}
            (out/f'phase-{index}.owner.safe.json').write_text(json.dumps(owner,sort_keys=True));code=child.wait();log.flush();os.fsync(log.fileno())
        phases.append(code)
        if code:break
    actual={};failed=[];errors=[];skipped=[];xmls={};fault_count_failures=[]
    for module in BUILT:
        for path in(snapshot/('src/schubert-nk-'+module+'/target/surefire-reports')).glob('TEST-*.xml'):
            tree=ET.parse(path).getroot();name=tree.get('name');xmls[name]=sha(path)
            if name in actual:raise ValueError('duplicate selected suite')
            actual[name]=set()
            for case in tree.findall('testcase'):
                method=case.get('name','').removesuffix('()')
                if method in actual[name]:raise ValueError('duplicate selected case')
                actual[name].add(method)
                if case.find('failure')is not None:
                    failed.append([name,method]);failure=case.find('failure')
                    if failure.get('type')=='org.opentest4j.AssertionFailedError'and failure.get('message')=='native acquisition before scratch failure ==> expected: <0> but was: <1>':fault_count_failures.append([name,method])
                if case.find('error')is not None:errors.append([name,method])
                if case.find('skipped')is not None:skipped.append([name,method])
    inventory=actual==expected
    red_expected=sorted([[PACKAGE+'SnapshotScratchOwnershipTest',name]for name in FAULT if name.startswith(('scratch001','scratch002'))])
    red=inventory and not errors and not skipped and sorted(failed)==red_expected and sorted(fault_count_failures)==red_expected
    static={};target_counters={}
    for module in BUILT:
        root=snapshot/('src/schubert-nk-'+module+'/target')
        report=root/'spotbugsXml.xml'
        if report.exists():static[module]=len(ET.parse(report).getroot().findall('BugInstance'))
        if module=='api'and(root/'site/jacoco/jacoco.xml').exists():
            for entry in ET.parse(root/'site/jacoco/jacoco.xml').getroot().findall('package/class'):
                if entry.get('name')==PACKAGE.replace('.','/')+'ResponseSnapshotCodec':target_counters={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}for c in entry.findall('counter')}
    fixed=all(sha(snapshot/name)==digest for name,digest in inputs.items())and subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==head and not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
    reference=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5414-current3896-cases/qualification.json'
    if sha(reference)!='273d2710743c5da8d45918feb4dc9542ad2043306efce0a29f4ca18d5c16a56f':raise ValueError('fixed actual296 compiled qualification first')
    q=json.loads(reference.read_bytes())
    if q['productionSource']!=BASE or q['mainClasses']!=1664:raise ValueError('actual1664 same base source')
    before={k:v for k,v in q['allPhysicalMainSha256'].items()if k.split(':',1)[0]in BUILT}
    physical={module+':'+p.relative_to(snapshot/('src/schubert-nk-'+module+'/target/classes')).as_posix():sha(p)for module in BUILT for p in(snapshot/('src/schubert-nk-'+module+'/target/classes')).rglob('*.class')}
    changed=sorted(k for k in physical.keys()&before.keys()if physical[k]!=before[k]);added=sorted(physical.keys()-before.keys());removed=sorted(before.keys()-physical.keys())
    expected_changes=[]if args.phase=='red'else['api:'+PACKAGE.replace('.','/')+'ResponseSnapshotCodec.class']
    physical_ok=changed==expected_changes and not added and not removed
    red=red and physical_ok and fixed and phases==[0,1]
    target100=all(target_counters.get(k,{}).get('missed')==0 and target_counters.get(k,{}).get('covered',0)>0 for k in('LINE','METHOD','CLASS','BRANCH'))
    green=inventory and not failed and not errors and not skipped and phases==[0,0]and set(static)==set(BUILT)and not any(static.values())and fixed and physical_ok and target100
    value={'actualExit':next((x for x in phases if x),0),'sourceSnapshot':head,'baseProductionSource':BASE,'phase':args.phase,
        'startedUTC':started,'completedUTC':utc(),'phaseExits':phases,'sourceFixed':fixed,'expectedCases':sum(map(len,expected.values())),
        'actualCases':sum(map(len,actual.values())),'suites':len(actual),'exactSelectedInventory':inventory,'failed':failed,'errors':errors,'skipped':skipped,
        'purposefulRedEstablished':red,'greenSelectedQualified':green,'staticBuiltModules':static,'targetCounters':target_counters,
        'xmlHashes':xmls,'commands':commands,'archiveSha256':sha(archive),'formalAccepted':False,'coverageWholeAccepted':False,'vmActions':0,'oldNativeImported':False,
        'physicalMain':{'count':len(physical),'changed':changed,'added':added,'removed':removed,'declaredDeltaQualified':physical_ok,'sha256':physical},'targetFour100':target100,
        'caseScope':{'fault':4,'codec':7 if args.phase=='green'else 0,'necessaryDependencyContracts':18},'noTestsGuardSuppressed':False}
    with(out/'manifest.safe.json').open('x')as target:json.dump(value,target,sort_keys=True);target.flush();os.fsync(target.fileno())
    print(json.dumps({k:value[k]for k in('actualExit','phase','sourceFixed','expectedCases','actualCases','suites','exactSelectedInventory','failed','errors','skipped','purposefulRedEstablished','greenSelectedQualified','staticBuiltModules','targetCounters','targetFour100','formalAccepted')},sort_keys=True))
    return value['actualExit']or(0 if green or red else 1)


if __name__=='__main__':raise SystemExit(main())
