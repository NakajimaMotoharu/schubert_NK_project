"""Read-only original authentication JDBC run reconciliation; never invokes Product/tests."""
from pathlib import Path
import datetime, hashlib, json, re, subprocess, zipfile, xml.etree.ElementTree as E
from source_evidence_binding import bind_named_sources
from pmo_port_report import project_port
root=Path.cwd();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
source='5720b037554171d092eddabcf0a04bfe95897350';core='fb189b11ee9dc39a5ef269f4018b809439cfc0f9';verifier='6d9ccf9ff77358d730c0a4a533bb422a20886614'
pub=Path('evidence/01_PT/007_NK-AUT-001/evidence/PG20914-session-issue-jdbc-eight-v1');m=load(pub/'manifest.json');assert sha(pub/'manifest.json')=='b51345dd72a3a46cf9d8ead259b301c442c1de7dba965ec75cb3ad7d190554ed'
projection=project_port(m,dict(source=source,tests=8,physical=1,four=[69,3,1,20]));assert m['productionCoreMain']==core
for name,h in m['files'].items():assert '/' not in name and sha(pub/name)==h
names=['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthSessionService.java','src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/SessionIssueJdbcPortTest.java']
bind_named_sources(root,m['inputHashes'],names,names)
for name in names:assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+name])).hexdigest()==m['inputHashes'][name]
slot=Path(m['originalManifest']['path']).parent;raw=load(slot/'manifest.safe.json');assert sha(slot/'manifest.safe.json')==m['originalManifest']['sha256'] and raw['actualExit']==0 and raw['begin']['source']==source
for stage in raw['stages'].values():assert stage['actualExit']==0 and not stage['timedOut']
for key,pinned in [('producerGitArtifact',source),('verifierGitArtifact',verifier)]:
 item=m[key];assert item['source']==pinned and hashlib.sha256(subprocess.check_output(['git','show',pinned+':'+item['path']])).hexdigest()==item['sha256']
assert raw['begin']['driverSha256']==m['producerGitArtifact']['sha256']
cfgPath=Path('evidence/01_PT/018_NK-OPS-001/input/092_session_issue_jdbc.json');assert hashlib.sha256(json.dumps(load(cfgPath),sort_keys=True).encode()).hexdigest()==raw['begin']['configHash']==m['configHash'] and hashlib.sha256(subprocess.check_output(['git','show',source+':'+str(cfgPath)])).hexdigest()==sha(cfgPath)
actual=[];environment=[]
for p in sorted((slot/'xml').glob('TEST-*.xml')):
 tree=E.parse(p).getroot();assert all(int(tree.get(k,'0'))==0 for k in ('failures','errors','skipped'));assert not tree.findall('.//failure') and not tree.findall('.//error') and not tree.findall('.//skipped')
 for case in tree.findall('testcase'):
  if 'SessionIssueJdbcPortTest' in case.get('classname',''):actual.append((case.get('classname'),case.get('name').removesuffix('()')))
 props={x.get('name'):x.get('value') for x in tree.findall('properties/property')};assert props['java.io.tmpdir']==str(slot/'tmp')
 environment.append({k:props.get(k) for k in ['os.name','os.arch','os.version','java.version','java.vendor']})
assert sorted(actual)==sorted(map(tuple,m['selectedTestMethods'])) and len(actual)==8
spec=Path('evidence/01_PT/007_NK-AUT-001/045_DIF016session発行自己所有境界単体仕様.md').read_text();pairs=re.findall(r'\|(PT-AUT-ISS\d{3})\|(\w+)\|',spec);assert len(pairs)==8 and {n for _,n in pairs}=={n for _,n in actual}
coverage={c.get('name'):{x.get('type'):{'covered':int(x.get('covered')),'missed':int(x.get('missed'))} for x in c.findall('counter')} for c in E.parse(slot/'coverage.xml').getroot().findall('.//package/class')};assert coverage==m['coverage']
normal=load(root.parent/'pgpt-runs/PG379/pg20704-media-css-six-main-resource-compile-v1/manifest.safe.json');assert normal['source']==core and normal['actualExit']==0
api=normal['jars']['api'];assert sha(api['path'])==api['sha256']
with zipfile.ZipFile(api['path']) as archive:
 for name,h in m['physicalHashes'].items():assert hashlib.sha256(archive.read(name+'.class')).hexdigest()==h
execText=(slot/'execinfo.stdout').read_text();assert execText.count('Session "')==1 and 'Session "'+m['session']+'"' in execText
for name,crc in m['physicalClassIds'].items():assert re.search(r'^'+crc+r'\s+\d+ of\s+\d+\s+'+re.escape(name)+r'$',execText,re.M)
review=m['jdkExceptionInitializationReview'];assert review['source']==verifier and review['testsReexecuted']==0 and sha(review['path'])==review['sha256']
static=Path('evidence/01_PT/007_NK-AUT-001/evidence/PG20910-session-issue-style-static-v1/manifest.json');s=load(static);assert s['pmdRaw']==5 and s['applicableViolations']==s['checkstyle']==s['processingErrors']==0
golden=Path('evidence/01_PT/007_NK-AUT-001/evidence/PG20902-session-public-golden-vectors-v1/manifest.json');assert sha(golden)=='19e53c2f86c9dc391b733f1a53621c50d40e98920bbf8e9fbf404a6bea4bbb5c';g=load(golden);assert g['syntheticPublicOnly'] and not g['actualCredential'] and all(v['envelopeHex'] in Path(names[1]).read_text() for v in g['vectors'].values())
out=Path('evidence/01_PT/007_NK-AUT-001/evidence/PG20920-session-issue-independent-post-v1');assert not out.exists();out.mkdir()
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=source,productionCoreMain=core,verifierSource=verifier,originalPost=dict(path=str(pub/'manifest.json'),sha256=sha(pub/'manifest.json')),tests=8,projection=projection,physicalNormalClassHashes=m['physicalHashes'],sourceTestIds=pairs,checks=['original terminal/stages0','6 XML method bijection/FES0','all public artifact hashes','explicit Main/Test Git pins','separate producer/verifier/config Git pins','2physical normal jar bytes/CRC/session','four counters69/3/1/20 miss0','SDK exact original review','static raw5 individually nonapplicable','heldFourZero/no union/no manual exclusion'],staticPost=dict(path=str(static),sha256=sha(static)),environment=environment,productTestsReexecuted=0,reusedCheckerTemplate='008 previously corrected canonical-config and physical-Git-pin semantics; its old prototype failure does not belong to this run',checkerSourceState='CURRENT_WIP_METADATA_ONLY_PUBLISHED_NEXT_NOT_PRODUCT_SOURCE',checkerSha256=sha(__file__),independentGolden=dict(path=str(golden),sha256=sha(golden)),actualLiveSessionIssued=False,formalUpdated=False,newAcceptance=0,effortRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,testsReexecuted=0,tests=8,manifestSha256=sha(out/'manifest.json'))))
