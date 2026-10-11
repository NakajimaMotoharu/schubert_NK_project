"""Same-Main technical counter graph plus PG1485 latest Inspector only; not formal."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from pg1485_inspector_closing_qualification import SOURCE,W,sha,require

MANIFESTS={
 'pg1428-publication-partial-counter-v1':'9b4cc00907345c13d9235fe0dbe05bd6293f69521e6ecfaf42bfa82b08048312',
 'pg1341-published-eight-native-v1':'99ace9ae4497d33c331700ec656502e543de2e64192ba5350b4f1dfa456f4d71',
 'pg1401-current-bootstrap-ten-native-v1':'c05911e9ddbf292c2375d155166fc8602bcc41345de47a15e8b7f723efdd1502',
 'pg1409-batch-boundary-selected-v1':'6fe5deb4c97ec31066fd4eac6091ddc8323acbb30478255c46a241c5c6ff981b',
 'pg1414-batch-boundary-selected-v1':'c309cb35a325b6837f196fb5373059a2d670c67241657e48fd6ca27310e1b185',
 'pg1422-batch-boundary-selected-v1':'93e479448dae323e9a7fd4e8f91b3e409f34881f4e719e2cf54764311bd71dab',
 'pg1426-batch-boundary-selected-v1':'bed0d0e106ffa4204b2218782a4252d967297d23d9b85e671a82a41d667b4cc4'}

def qualified_inspector(new):
    require(type(new)is dict and type(new.get('actualExit'))is int and new['actualExit']==0 and new.get('productionSource')==SOURCE and type(new.get('classByteMismatch'))is int and new['classByteMismatch']==0 and new.get('terminalRetainedNotSelected')is True and new.get('sameSessionUnion0')is True)
    proof=new.get('closingOracle');require(type(proof)is dict and all(proof.get(k)is True for k in ('sameSession','probeMonotonic','latestClosingOnly')))

def input_graph():
    known={}
    for name,digest in MANIFESTS.items():
        p=W/name/'manifest.safe.json';require(sha(p)==digest);v=json.loads(p.read_bytes())
        require(v['actualExit']==0 and v.get('productionSource',v.get('productionMainSource'))==SOURCE);known[name]=v
    root=known['pg1341-published-eight-native-v1'];host=W/'pg1279-held-channel-six-host-v1';h=json.loads((host/'manifest.safe.json').read_bytes());require(h['candidateSource']==SOURCE)
    data=[]
    def add(p,digest):require(sha(p)==digest);data.append(p)
    for module,digest in root['hostExecHashes'].items():
        require(digest==h['moduleResults'][module]['execSha256']);add(host/module/'jacoco.exec',digest)
    for i,record in enumerate(root['selected']):add(W/'pg1341-published-eight-native-v1'/(str(i)+'.exec'),record['sha256'])
    admin=known['pg1401-current-bootstrap-ten-native-v1'];add(W/'pg1401-current-bootstrap-ten-native-v1/bootstrap-1.exec',admin['bootstrapNativeHashes'][1])
    for name in ('pg1409-batch-boundary-selected-v1','pg1414-batch-boundary-selected-v1','pg1422-batch-boundary-selected-v1','pg1426-batch-boundary-selected-v1'):add(W/name/'selected.exec',known[name]['execSha256'])
    require(len(data)==19)
    inspector=W/'pg1485-inspector-closing-qualification-v1';new=json.loads((inspector/'manifest.safe.json').read_bytes())
    qualified_inspector(new)
    add(inspector/'closing.exec',new['nativeHashes']['closing.exec'])
    require(len(data)==20 and len(set(data))==20 and inspector/'terminal.exec'not in data and W/'pg1401-current-bootstrap-ten-native-v1/bootstrap-0.exec'not in data)
    return data,h,known['pg1428-publication-partial-counter-v1'],sha(inspector/'manifest.safe.json')

def main():
    os.umask(0o077);out=W/'pg1486-inspector-latest-counter-v1';out.mkdir(mode=0o700)
    data,h,prior,new_sha=input_graph();start=datetime.datetime.now(datetime.timezone.utc)
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository');libs=[]
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/jacoco/org.jacoco.report/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
        found=list(repo.glob(pattern));require(len(found)==1);libs.append(str(found[0]))
    cp=':'.join(libs);java='/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java'
    helper=W/'pg571-current-ten-native-v2/classes';xmlhelper=W/'pg1402-current-admin-native-gap-v1/classes'
    require(sha(helper/'NativeCoverage.class')=='37227f2f494bf2cc8e36eb52ba47c65af3e79ccaeb0c3efcb1fdf9f5d3e0af5a' and sha(xmlhelper/'NativeCoverageXml471.class')=='022716de432254edbc4a085a1d7c0a8e7e3a8cef31cdfbc7639479d308cc998b')
    counters={};host=W/'pg1279-held-channel-six-host-v1'
    for module in ('protocol','storage','bootstrap','api','web','batch'):
        jar=host/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');require(sha(jar)==h['moduleResults'][module]['jarSha256'])
        r=subprocess.run([java,'-cp',str(helper)+':'+cp,'NativeCoverage',str(jar),*map(str,data)],capture_output=True,timeout=45)
        (out/(module+'.private.log')).write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr)
        v=json.loads(r.stdout);require(v['classByteMismatch']==0);counters[module]=v
    kinds=('LINE','METHOD','CLASS','BRANCH');remaining={k:sum(v[k]['missed']for v in counters.values())for k in kinds};gain={k:prior['remaining'][k]-remaining[k]for k in kinds}
    require(all(v>=0 for v in gain.values()))
    xml=out/'batch.xml';jar=host/'batch/schubert-nk-batch-0.1.0-SNAPSHOT.jar'
    r=subprocess.run([java,'-cp',str(xmlhelper)+':'+cp,'NativeCoverageXml471',str(jar),str(xml),*map(str,data)],capture_output=True,timeout=45)
    (out/'xml.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr and b'classMismatch0=true'in r.stdout)
    tree=ET.parse(xml).getroot();require({c.attrib['type']:{'missed':int(c.attrib['missed']),'covered':int(c.attrib['covered'])}for c in tree.findall('counter')if c.attrib['type']in kinds}=={k:counters['batch'][k]for k in kinds})
    manifest={'run':'PG1486-inspector-latest-counter-v1','actualExit':0,'productionMainSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'startUTC':start.isoformat(),'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputHashes':{str(p.relative_to(W)):sha(p)for p in data},'priorManifestSha256':MANIFESTS['pg1428-publication-partial-counter-v1'],'inspectorQualificationManifestSha256':new_sha,'totalExecInputs':20,'sameSessionUnion0':True,'terminalRetainedNotSelected':True,'moduleCounters':counters,'remaining':remaining,'gainVs1428':gain,'batchXmlSha256':sha(xml),'formalAccepted':False,'freshWholeSameRunAccepted':False,'coverage100':all(v==0 for v in remaining.values()),'vmActions0':True}
    with(out/'manifest.safe.json').open('x')as f:json.dump(manifest,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:manifest[k]for k in ('actualExit','remaining','gainVs1428','formalAccepted','coverage100')}));return 0

if __name__=='__main__':raise SystemExit(main())
