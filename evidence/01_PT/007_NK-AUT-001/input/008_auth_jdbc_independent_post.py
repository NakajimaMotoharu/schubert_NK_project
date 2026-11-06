"""Read-only original authentication JDBC run reconciliation; never invokes Product/tests."""
from pathlib import Path
import datetime, hashlib, json, re, subprocess, zipfile, xml.etree.ElementTree as E
from source_evidence_binding import bind_named_sources
from pmo_port_report import project_port, port_check_labels, validate_port_check_labels
root=Path.cwd();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
source='f16526371daf0352925fda5c9686425a64e4a40b';core='fb189b11ee9dc39a5ef269f4018b809439cfc0f9';verifier='f34a61fdde299e134f016c31164ea93d4af192f6'
pub=Path('evidence/01_PT/007_NK-AUT-001/evidence/PG20840-authentication-verifier-jdbc-six-v1');m=load(pub/'manifest.json');assert sha(pub/'manifest.json')=='9ed3f1b415ee21c3439a2be2aa554692ea51f5509c507ebbd3c1d5c51f5adc03'
projection=project_port(m,dict(source=source,tests=6,physical=2,four=[66,6,2,25]));assert m['productionCoreMain']==core
for name,h in m['files'].items():assert '/' not in name and sha(pub/name)==h
names=['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthenticationContextVerifier.java','src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthenticationVerifierJdbcPortTest.java']
bind_named_sources(root,m['inputHashes'],names,names)
for name in names:assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+name])).hexdigest()==m['inputHashes'][name]
slot=Path(m['originalManifest']['path']).parent;raw=load(slot/'manifest.safe.json');assert sha(slot/'manifest.safe.json')==m['originalManifest']['sha256'] and raw['actualExit']==0 and raw['begin']['source']==source
for stage in raw['stages'].values():assert stage['actualExit']==0 and not stage['timedOut']
for key,pinned in [('producerGitArtifact',source),('verifierGitArtifact',verifier)]:
 item=m[key];assert item['source']==pinned and hashlib.sha256(subprocess.check_output(['git','show',pinned+':'+item['path']])).hexdigest()==item['sha256']
assert raw['begin']['driverSha256']==m['producerGitArtifact']['sha256']
cfgPath=Path('evidence/01_PT/018_NK-OPS-001/input/090_authentication_verifier_jdbc.json');assert hashlib.sha256(json.dumps(load(cfgPath),sort_keys=True).encode()).hexdigest()==raw['begin']['configHash']==m['configHash'] and hashlib.sha256(subprocess.check_output(['git','show',source+':'+str(cfgPath)])).hexdigest()==sha(cfgPath)
actual=[];environment=[]
for p in sorted((slot/'xml').glob('TEST-*.xml')):
 tree=E.parse(p).getroot();assert all(int(tree.get(k,'0'))==0 for k in ('failures','errors','skipped'));assert not tree.findall('.//failure') and not tree.findall('.//error') and not tree.findall('.//skipped')
 for case in tree.findall('testcase'):
  if 'AuthenticationVerifierJdbcPortTest' in case.get('classname',''):actual.append((case.get('classname'),case.get('name').removesuffix('()')))
 props={x.get('name'):x.get('value') for x in tree.findall('properties/property')};assert props['java.io.tmpdir']==str(slot/'tmp')
 environment.append({k:props.get(k) for k in ['os.name','os.arch','os.version','java.version','java.vendor']})
assert sorted(actual)==sorted(map(tuple,m['selectedTestMethods'])) and len(actual)==6
spec=Path('evidence/01_PT/007_NK-AUT-001/041_AuthenticationVerifier自己所有JDBC境界単体仕様.md').read_text();pairs=re.findall(r'\|(PT-AUT-JDBC\d{3})\|(\w+)\|',spec);assert len(pairs)==6 and {n for _,n in pairs}=={n for _,n in actual}
coverage={c.get('name'):{x.get('type'):{'covered':int(x.get('covered')),'missed':int(x.get('missed'))} for x in c.findall('counter')} for c in E.parse(slot/'coverage.xml').getroot().findall('.//package/class')};assert coverage==m['coverage']
normal=load(root.parent/'pgpt-runs/PG379/pg20704-media-css-six-main-resource-compile-v1/manifest.safe.json');assert normal['source']==core and normal['actualExit']==0
api=normal['jars']['api'];assert sha(api['path'])==api['sha256']
with zipfile.ZipFile(api['path']) as archive:
 for name,h in m['physicalHashes'].items():assert hashlib.sha256(archive.read(name+'.class')).hexdigest()==h
execText=(slot/'execinfo.stdout').read_text();assert execText.count('Session "')==1 and 'Session "'+m['session']+'"' in execText
for name,crc in m['physicalClassIds'].items():assert re.search(r'^'+crc+r'\s+\d+ of\s+\d+\s+'+re.escape(name)+r'$',execText,re.M)
review=m['jdkExceptionInitializationReview'];assert review['source']==verifier and review['testsReexecuted']==0 and sha(review['path'])==review['sha256']
static=Path('evidence/01_PT/007_NK-AUT-001/evidence/PG20838-auth-jdbc-style-static-v1/manifest.json');s=load(static);assert s['pmdRaw']==4 and s['applicableViolations']==s['checkstyle']==s['processingErrors']==0
out=Path('evidence/01_PT/007_NK-AUT-001/evidence/PG20850-authentication-jdbc-independent-post-v1');assert not out.exists();out.mkdir()
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=source,productionCoreMain=core,verifierSource=verifier,originalPost=dict(path=str(pub/'manifest.json'),sha256=sha(pub/'manifest.json')),tests=6,projection=projection,physicalNormalClassHashes=m['physicalHashes'],sourceTestIds=pairs,checks=port_check_labels(projection, s['pmdRaw']),staticPost=dict(path=str(static),sha256=sha(static)),environment=environment,productTestsReexecuted=0,initialMetadataDevelopmentAttempt={'actualExit':1,'reason':'New checker initially compared physical JSON bytes with producer canonical JSON digest; corrected to compare both semantics hash and frozen file Git hash before first delivery','productTestsReexecuted':0},checkerSourceState='CURRENT_WIP_METADATA_ONLY_PUBLISHED_NEXT_NOT_PRODUCT_SOURCE',checkerSha256=sha(__file__),formalUpdated=False,newAcceptance=0,effortRate=None)
validate_port_check_labels(projection, s['pmdRaw'], value['checks']);(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,testsReexecuted=0,tests=6,manifestSha256=sha(out/'manifest.json'))))
