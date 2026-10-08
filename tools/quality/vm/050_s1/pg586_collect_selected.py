"""Seal two actually selected classes; dependency-build skips never count as PT success."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import xml.etree.ElementTree as ET
import zipfile

T=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
J=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    run=W/'pg586-access-selected-v3';source=(run/'source').read_text().strip()
    assert source=='55363131eb0d071869c48c8468a7aa1be0724ea9'and(run/'exit').read_bytes()==b'0\n'
    entries=[line.split('  ',1)for line in(run/'source-files.sha256').read_text().splitlines()];assert entries
    objects=subprocess.check_output(['git','cat-file','--batch'],input=''.join(source+':'+name+'\n'for _,name in entries).encode(),cwd=T);offset=0
    for expected,name in entries:
        end=objects.index(b'\n',offset);header=objects[offset:end].split();assert len(header)==3 and header[1]==b'blob';size=int(header[2]);offset=end+1
        raw=objects[offset:offset+size];assert hashlib.sha256(raw).hexdigest()==expected and objects[offset+size:offset+size+1]==b'\n';offset+=size+1
    assert offset==len(objects)
    log=(run/'build.private.log').read_text();assert log.count('BUILD SUCCESS')==2 and 'BUILD FAILURE'not in log
    start=datetime.datetime.fromisoformat((run/'started').read_text().strip()).timestamp();end=datetime.datetime.fromisoformat((run/'completed').read_text().strip()).timestamp()
    tests={};hashes={}
    for cls,expected in [('MorningDatabaseAccessContractTest',7),('MorningDatabaseSessionTest',20)]:
        name='TEST-dev.codex.schubert.nk.batch.repository.'+cls+'.xml';p=run/name;original=T/'src/schubert-nk-batch/target/surefire-reports'/name
        assert sha(p)==sha(original)and start<=original.stat().st_mtime<=end+1
        suite=ET.parse(p).getroot();assert int(suite.attrib['tests'])==expected and all(int(suite.get(k,'0'))==0 for k in('failures','errors','skipped'))
        cases=suite.findall('testcase');assert len(cases)==expected and all(not any(c.find(k)is not None for k in('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError'))for c in cases)
        tests[cls]=expected;hashes[name]=sha(p)
    modules=('protocol','storage','bootstrap','api','web','batch');old=W/'pg585-access-reactor-v3';classes=0
    for m in modules:
        jar='schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar';paths=[old/m/jar,T/'src'/('schubert-nk-'+m)/'target'/jar,pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository/dev/codex/schubert')/('schubert-nk-'+m)/'0.1.0-SNAPSHOT'/jar]
        contents=[]
        for p in paths:
            with zipfile.ZipFile(p)as z:contents.append({n:z.read(n)for n in z.namelist()if n.endswith('.class')})
        assert contents[0]==contents[1]==contents[2]and contents[0];classes+=len(contents[0])
    assert not ET.parse(run/'spotbugsXml.xml').getroot().findall('.//BugInstance')
    cp=[str(W/'pg571-current-ten-native-v2/classes')];repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    for pattern in('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
        paths=list(repo.glob(pattern));assert len(paths)==1;cp.append(str(paths[0]))
    cohort=W/'pg581-current-eighteen-native-v3';eighteen=json.loads((cohort/'manifest.safe.json').read_bytes());prior=W/'pg561-current-native-v2';nine=json.loads((prior/'manifest.safe.json').read_bytes());data=[old/m/'jacoco.exec'for m in modules]
    for i,v in enumerate(nine['currentNativeFiles']):
        p=prior/(str(i)+'.exec');assert sha(p)==v['sha256'];data.append(p)
    boot=W/'pg571-current-ten-native-v2/bootstrap.exec';assert sha(boot)=='0f8869c6ef5e43f9ce858bf08a7da0cc161dc51b329b2209ef62a5092ed1ad9e';data.append(boot)
    for i,v in enumerate(eighteen['newFiles']):
        p=cohort/(str(i)+'.exec');assert sha(p)==v['sha256'];data.append(p)
    data.append(run/'selected-batch.exec');assert len(data)==25
    jar=run/'schubert-nk-batch-0.1.0-SNAPSHOT.jar';r=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeCoverage',str(jar),*[str(p)for p in data]],capture_output=True,timeout=45)
    assert r.returncode==0 and not r.stderr;counter=json.loads(r.stdout);assert counter['classByteMismatch']==0
    full=json.loads((old/'manifest.safe.json').read_bytes());before=full['nativeDiagnosticCounters']['batch'];gains={k:before[k]['missed']-counter[k]['missed']for k in('LINE','METHOD','CLASS','BRANCH')}
    doc=ET.parse(run/'jacoco.xml').getroot();access=next(c for c in doc.findall('./package/class')if c.attrib['name']=='dev/codex/schubert/nk/batch/repository/MorningDatabaseSession$Access');access_counts={c.attrib['type']:{'missed':int(c.attrib['missed']),'covered':int(c.attrib['covered'])}for c in access.findall('counter')}
    result={'actualExit':0,'run':'PG586-access-selected-v3','operatorSource':source,'productionSource':full['productionSource'],'tests':tests,'selectedTests':27,'newTests':3,'FESFlaky':0,
            'dependencyBuildOnlyTestsNotAccepted':True,'outsideSelectedNotRunCredit0':True,'mainClassBytesEqualInstalledCurrentPG585':classes,'selectedXmlHashes':hashes,
            'accessCounters':access_counts,'batchByteAlignedDiagnosticCounters':counter,'gainsVsPG585':gains,'hostNativeUnionDiagnosticOnly':True,
            'started':(run/'started').read_text().strip(),'completed':(run/'completed').read_text().strip(),'elapsedSeconds':end-start,
            'sourceFilesSha256':sha(run/'source-files.sha256'),'logSha256':sha(run/'build.private.log'),'selectedExecSha256':sha(run/'selected-batch.exec'),
            'collectorSourceSha256':sha(pathlib.Path(__file__)),'formalAccepted':False,'rawExported':False}
    with(run/'manifest.safe.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'selectedPT':27,'newTests':3,'sameMainClassBytes':classes,'gains':gains,'accessCounters':access_counts,'manifestSha256':sha(run/'manifest.safe.json'),'formalAccepted':False}))


if __name__=='__main__':main()
