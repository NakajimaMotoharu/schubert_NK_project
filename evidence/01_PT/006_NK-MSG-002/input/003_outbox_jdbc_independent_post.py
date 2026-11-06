"""Independently bind the existing nine-method Outbox proof; never invoke Product or tools."""
from pathlib import Path
import json,hashlib,subprocess,re,zipfile,datetime
import xml.etree.ElementTree as E
from pmo_port_report import project_port,port_check_labels,validate_port_check_labels
from source_evidence_binding import bind_named_sources
root=Path.cwd();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
source='03eeef1a3d6cfb93000641bcb87f83507a1f3f4d';core='4217e14083c6ecac116216e08d57f4361eb2f12d';verifier='ceacbb3c942a67c52fb8153be6bee134dfbfd859'
pub=Path('evidence/01_PT/006_NK-MSG-002/evidence/PG21014-outbox-null-oracle-nine-v1');m=load(pub/'manifest.json');assert sha(pub/'manifest.json')=='6bd69944333c32d39180928c51cfa00ba0b063af77cef142a4907e23c99b5685'
projection=project_port(m,dict(source=source,tests=9,physical=1,four=[122,11,1,32]));assert m['productionCoreMain']==core
for name,h in m['files'].items():assert '/' not in name and sha(pub/name)==h
prefix='src/schubert-nk-api/src/';pkg='java/dev/codex/schubert/nk/api/messaging/outbound/'
names=[prefix+'main/'+pkg+'JdbcOutboxRepository.java',*[prefix+'test/'+pkg+n+'.java' for n in ['JdbcOutboxPortTest','OutboxReturningIdContractTest']]]
bind_named_sources(root,m['inputHashes'],names,names)
for name in names:assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+name])).hexdigest()==m['inputHashes'][name]
slot=Path(m['originalManifest']['path']).parent;raw=load(slot/'manifest.safe.json');assert sha(slot/'manifest.safe.json')==m['originalManifest']['sha256'] and raw['actualExit']==0 and raw['begin']['source']==source
for stage in raw['stages'].values():assert stage['actualExit']==0 and not stage['timedOut']
for key,pinned in [('producerGitArtifact',source),('verifierGitArtifact',verifier)]:
 item=m[key];assert item['source']==pinned and hashlib.sha256(subprocess.check_output(['git','show',pinned+':'+item['path']])).hexdigest()==item['sha256']
assert raw['begin']['driverSha256']==m['producerGitArtifact']['sha256']
cfgPath=Path('evidence/01_PT/018_NK-OPS-001/input/096_outbox_jdbc.json');assert hashlib.sha256(json.dumps(load(cfgPath),sort_keys=True).encode()).hexdigest()==raw['begin']['configHash']==m['configHash'] and hashlib.sha256(subprocess.check_output(['git','show',source+':'+str(cfgPath)])).hexdigest()==sha(cfgPath)
actual=[];environment=[]
for p in sorted((slot/'xml').glob('TEST-*.xml')):
 tree=E.parse(p).getroot();assert all(int(tree.get(k,'0'))==0 for k in ('failures','errors','skipped'));assert not tree.findall('.//failure') and not tree.findall('.//error') and not tree.findall('.//skipped')
 for case in tree.findall('testcase'):actual.append((case.get('classname'),case.get('name').removesuffix('()')))
 props={x.get('name'):x.get('value') for x in tree.findall('properties/property')};assert props['java.io.tmpdir']==str(slot/'tmp');environment.append({k:props.get(k) for k in ['os.name','os.arch','os.version','java.version','java.vendor']})
assert sorted(actual)==sorted(map(tuple,m['selectedTestMethods'])) and len(actual)==len(set(actual))==9
spec=Path('evidence/01_PT/006_NK-MSG-002/007_JdbcOutbox自己所有境界単体仕様.md').read_text();pairs=re.findall(r'\|(PT-OUT-JDBC\d{3})\|(\w+)\|',spec);assert len(pairs)==9 and {n for _,n in pairs}=={n for _,n in actual}
coverage={c.get('name'):{x.get('type'):{'covered':int(x.get('covered')),'missed':int(x.get('missed'))} for x in c.findall('counter')} for c in E.parse(slot/'coverage.xml').getroot().findall('.//package/class')};assert coverage==m['coverage']
normal=load(root.parent/'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json');assert normal['source']==core and normal['actualExit']==0 and normal['classIdentity']['changedPhysical']==['api:dev/codex/schubert/nk/api/messaging/outbound/JdbcOutboxRepository.class']
assert normal['sourceInputsUnchanged'] and normal['classIdentity']['physicalClasses']==1844
for n,h in normal['begin']['inputHashes'].items():assert sha(n)==h
api=normal['jars']['api'];assert sha(api['path'])==api['sha256']
with zipfile.ZipFile(api['path']) as archive:
 for name,h in m['physicalHashes'].items():assert hashlib.sha256(archive.read(name+'.class')).hexdigest()==h
execText=(slot/'execinfo.stdout').read_text();assert execText.count('Session "')==1 and 'Session "'+m['session']+'"' in execText
for name,crc in m['physicalClassIds'].items():assert re.search(r'^'+crc+r'\s+\d+ of\s+\d+\s+'+re.escape(name)+r'$',execText,re.M)
review=m['jdkExceptionInitializationReview'];assert review['source']==verifier and review['testsReexecuted']==0 and sha(review['path'])==review['sha256']
static=Path('evidence/01_PT/006_NK-MSG-002/evidence/PG21012-outbox-null-oracle-static-v1/manifest.json');s=load(static);assert s['pmdRaw']==9 and s['applicableViolations']==s['checkstyle']==s['processingErrors']==0 and all(not row['applicable'] and row['reason'] for row in s['classification']);assert s['sourceInputs']==m['inputHashes']
sb=load(root.parent/'pgpt-runs/PG379/pg20992-outbox-required-six-static-reactor-v1/manifest.safe.json');assert sb['actualExit']==0 and sb['source']==core and len(sb['reports'])==6
for x in sb['reports'].values():assert sha(x['path'])==x['sha256'] and x['bugs']==x['missing']==x['errors']==0
oracle=Path('evidence/01_PT/006_NK-MSG-002/input/002_outbox_required_null_oracle.json');o=load(oracle);assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+str(oracle)])).hexdigest()==sha(oracle);assert o['expected']['sqlState']=='22004'
contract=o['requiredColumn'];assert sha(contract['path'])==contract['sha256']==hashlib.sha256(subprocess.check_output(['git','show',o['unchangedContractSource']+':'+contract['path']])).hexdigest()
checks=port_check_labels(projection,s['pmdRaw']);validate_port_check_labels(projection,s['pmdRaw'],checks)
out=Path('evidence/01_PT/006_NK-MSG-002/evidence/PG21028-outbox-jdbc-independent-post-v1');assert not out.exists();out.mkdir()
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=source,productionCoreMain=core,verifierSource=verifier,originalPost=dict(path=str(pub/'manifest.json'),sha256=sha(pub/'manifest.json')),tests=9,projection=projection,physicalNormalClassHashes=m['physicalHashes'],sourceTestIds=pairs,checks=checks,staticPost=dict(path=str(static),sha256=sha(static)),environment=environment,productTestsReexecuted=0,checkerSha256=sha(__file__),checkerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),requiredNullOracle=dict(path=str(oracle),sha256=sha(oracle)),actualDatabaseOrJmsOperation=False,formalUpdated=False,newAcceptance=0,effortRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,testsReexecuted=0,tests=9,manifestSha256=sha(out/'manifest.json'))))
