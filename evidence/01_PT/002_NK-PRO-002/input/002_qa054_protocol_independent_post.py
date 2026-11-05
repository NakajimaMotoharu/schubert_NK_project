"""Read-only independent qualification of an existing QA054 run; never invokes Product/JUnit."""
from pathlib import Path
import os,re,json,hashlib,subprocess,zipfile,xml.etree.ElementTree as E
import pg9666_pagination_static as runner
import jacoco_readonly_exec_subset as decoder
root=Path.cwd();runs=root.parent/'pgpt-runs/PG379';unit=runs/'pg19458-qa054-protocol-selected-unit-v1';slot=runs/'pg19462-qa054-protocol-independent-post-v1';assert not slot.exists();slot.mkdir();runner.SLOT=slot;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();m=json.loads((unit/'manifest.safe.json').read_text());b=m['begin'];assert m['actualExit']==0 and m['tests']==63 and all(m[k]==0 for k in ['failures','errors','skipped']);assert b['source']=='c11920fe9b556443e5509dfdd692adad11b53c35';assert b['coreSource']=='da176a90e7d59c23aaa50b2a00f42c200590b775'
for p,h in b['inputs'].items():assert hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+p])).hexdigest()==h
assert subprocess.check_output(['git','diff','--name-only',b['coreSource'],b['source'],'--','src/*/src/main','pom.xml','.mvn','mvnw'])==b''
for name,stage in m['stages'].items():
 assert stage['actualExit']==0 and not stage['timedOut'];assert sha(unit/(name+'.stdout'))==stage['stdoutSha256'];assert sha(unit/(name+'.stderr'))==stage['stderrSha256']
cmd=b['command'];assert cmd.count('--select-class')==13 and '--select-method' not in cmd;assert any('append=false' in x and 'sessionid='+b['session'] in x for x in cmd);assert not any('native-access' in x for x in cmd)
cp=cmd[cmd.index('--class-path')+1].split(os.pathsep);assert len(cp)==3 and cp[0].endswith('/test-classes') and cp[1].endswith('/schubert-nk-protocol-0.1.0-SNAPSHOT.jar') and cp[2].endswith('/jspecify-1.0.1.jar')
for p,h in b['dependencies'].items():assert sha(p)==h
jar=Path(cp[1]);physical=m['physicalHashes'];assert set(physical)=={'dev/codex/schubert/nk/protocol/'+n for n in ['layout/LayoutFieldCatalog','layout/LayoutFieldCatalog$1','layout/LayoutFieldCatalog$MutableFields','layout/PayloadSemanticValidator','layout/log/WebLogEventData','codec/PayloadCodec','codec/PayloadCodec$1']}
with zipfile.ZipFile(jar) as z:
 for name,h in physical.items():assert hashlib.sha256(z.read(name+'.class')).hexdigest()==h==sha(unit/'component'/(name+'.class'))
cli=root.parent/'toolchain/org.jacoco.cli-0.8.15-nodeps.jar';jdk=root.parent/'toolchain/jdk-25.0.4/bin/java';assert sha(cli)=='d2b74b20b415163c1f53261e7c5ef4445b788327094208ff821e0c2baf9bc8f1';stage=runner.step('classinfo',[str(jdk),'-jar',str(cli),'classinfo',str(unit/'component')],root);assert stage['actualExit']==0
ids={n:i.lstrip('0') or '0' for i,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(slot/'classinfo.stdout').read_text())};assert set(ids)==set(physical)
classes=E.parse(unit/'jacoco.xml').getroot().findall('package/class');executable={c.get('name') for c in classes if c.findall('counter')};assert len(executable)==5
parsed=decoder.decode((unit/'jacoco.exec').read_bytes(),executable);assert bytes.fromhex(parsed['sessions'][0]['labelBytesHex']).decode()==b['session'];assert all(parsed['classes'][n]['crc64']==ids[n] for n in executable)
for c in classes:
 if c.get('name') not in executable:
  assert not c.findall('method') and c.get('name').endswith('$1')
  from classfile_code_metadata import decode as classmeta
  metadata=classmeta((unit/'component'/(c.get('name')+'.class')).read_bytes(),c.get('name')+'.class');assert metadata['flags'] & 0x1000
 for counter in c.findall('counter'):assert int(counter.get('missed'))==0
coverage={k:sum(v.get(k,{}).get('covered',0) for v in m['coverage'].values()) for k in ['LINE','METHOD','CLASS','BRANCH']};assert list(coverage.values())==[661,89,5,400]
actual=set();xmlpins={};environment=[]
for p in sorted((unit/'xml').glob('TEST-*.xml')):
 xmlpins[str(p)]=sha(p);tree=E.parse(p);n=tree.getroot();props={x.get('name'):x.get('value') for x in n.findall('properties/property')};assert props.get('java.io.tmpdir')==str(unit/'tmp');environment.append({k:props.get(k) for k in ['java.version','java.vendor','os.name','os.arch','os.version']})
 for t in n.findall('testcase'):
  assert not any(t.findall(k) for k in ['failure','error','skipped']);name=t.get('name');assert name.endswith('()');actual.add((t.get('classname'),name[:-2]))
expected=set()
for cls in b['selectedClasses']:
 p='src/schubert-nk-protocol/src/test/java/'+cls.replace('.','/')+'.java';source=subprocess.check_output(['git','show',b['source']+':'+p]).decode();expected.update((cls,n) for n in re.findall(r'@Test\s*(?://[^\n]*\n\s*)?void\s+(\w+)\s*\(',source))
assert actual==expected and len(actual)==63
stdout=(unit/'unit.stdout').read_text()
for v in ['63 tests found','63 tests started','63 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert v in stdout
init=(unit/'class-init.log').read_text();held=['api/error/TemporaryInfrastructureException','web/bootstrap/WebStartupException','api/idempotency/FingerprintKeyRing','api/idempotency/ResponseSnapshotCodec'];assert all(x not in init for x in held);assert all(x not in init for x in ['schubert/nk/storage/','schubert/nk/batch/','org/apache/activemq/','org/postgresql/'])
# Preserve original REQUEST golden resource exactly; QA054 adds a separate independent vector.
p='src/schubert-nk-protocol/src/test/resources/protocol/payload-golden-ui234-236.tsv';assert subprocess.check_output(['git','show','11c10dab7039b6583abac88fdb2dd48a43a41389:'+p])==subprocess.check_output(['git','show',b['source']+':'+p])
result={'actualExit':0,'source':b['source'],'productionCoreMain':b['coreSource'],'originalManifestSha256':sha(unit/'manifest.safe.json'),'originalXmlPins':xmlpins,'tests':63,'failures':0,'errors':0,'skipped':0,'aborted':0,'physicalClassHashes':physical,'physicalClassIds':ids,'compilerSyntheticNoCode':sorted(set(physical)-executable),'executableClasses':5,'fourCounters':coverage,'singleExecSingleSession':True,'execDecoded':parsed,'allSelectedSourceTestMethods':sorted(actual),'heldFourInitializationHits':0,'environment':environment,'oldRequestGoldenUnchanged':True,'manualCoverageExclusions':[],'oldExecUnion':False,'global451Accepted':False,'formalUpdated':False,'newIndividualWbsAccepted':0,'toolSha256':sha(__file__),'classinfoToolSha256':sha(cli)};(slot/'manifest.safe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'actualExit':0,'tests':63,'fourCounters':coverage,'physical':len(physical),'manifestSha256':sha(slot/'manifest.safe.json')}))
