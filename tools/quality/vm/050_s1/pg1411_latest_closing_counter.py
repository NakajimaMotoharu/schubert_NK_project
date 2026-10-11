"""Independent monotonic proof and latest-only input; terminal kept but never unioned."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from pg1406_batch_boundary_selected import SOURCE,W,J,T,CHANGED

R=Path(__file__).resolve().parent

def require(v):
    if not v:raise ValueError('latest closing counter contract refused')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    os.umask(0o077);require(not subprocess.check_output(['git','status','--porcelain']))
    require(subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'],text=True).splitlines()==CHANGED)
    old=W/'pg1410-batch-selected-same-main-counter-v1';require(sha(old/'manifest.safe.json')=='e935faf3d347d5598aeaf53f53b2599e3184c0718aedcbc6e3d3cccc2aed3813');prior=json.loads((old/'manifest.safe.json').read_bytes())
    admin=W/'pg1401-current-bootstrap-ten-native-v1';root=W/'pg1341-published-eight-native-v1';host=W/'pg1279-held-channel-six-host-v1';selected=W/'pg1409-batch-boundary-selected-v1'
    a=json.loads((admin/'manifest.safe.json').read_bytes());e=json.loads((root/'manifest.safe.json').read_bytes());h=json.loads((host/'manifest.safe.json').read_bytes());s=json.loads((selected/'manifest.safe.json').read_bytes());post=json.loads((W/'pg1400-existing-admin-independent-post-v1.safe.json').read_bytes())
    require(sha(admin/'manifest.safe.json')==prior['previousNativeManifestSha256']and sha(selected/'manifest.safe.json')==prior['selectedManifestSha256'])
    require(a['productionSource']==e['productionSource']==s['productionMainSource']==h['candidateSource']==SOURCE and post['actualExit']==0)
    for i,d in enumerate(a['bootstrapNativeHashes']):require(sha(admin/('bootstrap-'+str(i)+'.exec'))==d)
    require(post['bootstrap']['files'][0]['relative'].endswith('.terminal.exec')and post['bootstrap']['files'][1]['relative'].endswith('.closing.exec'))
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository');libraries=[]
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/jacoco/org.jacoco.report/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
        v=list(repo.glob(pattern));require(len(v)==1);libraries.append(str(v[0]))
    run=W/'pg1411-latest-closing-counter-v1';run.mkdir(mode=0o700);classes=run/'classes';classes.mkdir(mode=0o700)
    cp=':'.join(libraries);start=datetime.datetime.now(datetime.timezone.utc)
    with(run/'oracle.private.log').open('xb')as log:
        for args in ([str(J/'bin/javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(R/'NativeClosingSelect1411.java'),str(R/'NativeClosingSelect1411Test.java')],[str(J/'bin/java'),'-cp',str(classes)+':'+cp,'NativeClosingSelect1411Test']):
            r=subprocess.run(args,stdout=log,stderr=log);require(r.returncode==0)
    m=post['bootstrap'];r=subprocess.run([str(J/'bin/java'),'-cp',str(classes)+':'+cp,'NativeClosingSelect1411',str(admin/'bootstrap-0.exec'),str(admin/'bootstrap-1.exec'),str(m['lowerMs']),str(m['upperMs'])],capture_output=True)
    with(run/'actual-monotonic.private.log').open('xb')as f:f.write(r.stdout+r.stderr)
    require(r.returncode==0 and not r.stderr);proof=json.loads(r.stdout);require(proof['sameSession']is True and proof['probeMonotonic']is True and proof['latestClosingOnly']is True)
    modules=('protocol','storage','bootstrap','api','web','batch');data=[]
    for name in modules:
        p=host/name/'jacoco.exec';require(sha(p)==e['hostExecHashes'][name]==h['moduleResults'][name]['execSha256']);data.append(p)
    for i,v in enumerate(e['selected']):
        p=root/(str(i)+'.exec');require(sha(p)==v['sha256']);data.append(p)
    data.append(admin/'bootstrap-1.exec');data.append(selected/'selected.exec')
    require(len(data)==16 and admin/'bootstrap-0.exec'not in data and sha(selected/'selected.exec')==s['execSha256'])
    helper=W/'pg571-current-ten-native-v2/classes';xml_helper=W/'pg1402-current-admin-native-gap-v1/classes'
    require(sha(helper/'NativeCoverage.class')=='37227f2f494bf2cc8e36eb52ba47c65af3e79ccaeb0c3efcb1fdf9f5d3e0af5a'and sha(xml_helper/'NativeCoverageXml471.class')=='022716de432254edbc4a085a1d7c0a8e7e3a8cef31cdfbc7639479d308cc998b')
    counters={}
    for module in modules:
        jar=host/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');require(sha(jar)==h['moduleResults'][module]['jarSha256'])
        r=subprocess.run([str(J/'bin/java'),'-cp',str(helper)+':'+cp,'NativeCoverage',str(jar),*map(str,data)],capture_output=True,timeout=45)
        with(run/(module+'.private.log')).open('xb')as f:f.write(r.stdout+r.stderr)
        require(r.returncode==0 and not r.stderr);v=json.loads(r.stdout);require(v['classByteMismatch']==0);counters[module]=v
    require(counters==prior['moduleCounters'])
    xml=run/'batch.xml';jar=host/'batch/schubert-nk-batch-0.1.0-SNAPSHOT.jar'
    r=subprocess.run([str(J/'bin/java'),'-cp',str(xml_helper)+':'+cp,'NativeCoverageXml471',str(jar),str(xml),*map(str,data)],capture_output=True,timeout=45)
    with(run/'xml.private.log').open('xb')as f:f.write(r.stdout+r.stderr)
    require(r.returncode==0 and not r.stderr and b'classMismatch0=true'in r.stdout)
    tree=ET.parse(xml).getroot();kinds=('LINE','METHOD','CLASS','BRANCH')
    require({v.attrib['type']:{'missed':int(v.attrib['missed']),'covered':int(v.attrib['covered'])}for v in tree.findall('counter')if v.attrib['type']in kinds}=={k:counters['batch'][k]for k in kinds})
    closed={}
    for c in tree.findall('package/class'):
        if c.attrib['name']in ('dev/codex/schubert/nk/batch/repository/BatchRunRepository','dev/codex/schubert/nk/batch/backup/BackupProfile'):
            counts={n.attrib['type']:int(n.attrib['missed'])for n in c.findall('counter')};require(all(counts[k]==0 for k in kinds));closed[c.attrib['name']]=counts
    require(len(closed)==2)
    record={'run':'PG1411-latest-closing-counter-v1','actualExit':0,'productionMainSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'startedUTC':start.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'closingOracle':proof,'oracleLogSha256':sha(run/'oracle.private.log'),'actualMonotonicLogSha256':sha(run/'actual-monotonic.private.log'),'capturedNativeStreams':10,'selectedNativeStreams':9,'totalExecInputs':16,'terminalRetainedNotSelected':True,'sameSessionUnion0':True,'allSixCountersEqualPriorUnionDiagnostic':True,'moduleCounters':counters,'remaining':prior['remaining'],'newCounterClosedClasses':closed,'batchXmlSha256':sha(xml),'selectedExecSha256':s['execSha256'],'freshSelectedTests':24,'newTestMethods':3,'formalAccepted':False,'coverage100':False,'freshWholeRunClaimed':False,'vmActions0':True}
    with(run/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:record[k]for k in ('actualExit','selectedNativeStreams','sameSessionUnion0','allSixCountersEqualPriorUnionDiagnostic','remaining','newCounterClosedClasses','formalAccepted')}));return 0

if __name__=='__main__':raise SystemExit(main())
