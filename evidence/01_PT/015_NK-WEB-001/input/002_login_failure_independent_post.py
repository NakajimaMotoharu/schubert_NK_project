"""Bind original Login-failure HTTP callback proof; no Product or tools execution."""
from pathlib import Path
import json,hashlib,subprocess,re,zipfile,datetime
import xml.etree.ElementTree as E
from pmo_port_report import project_port,port_check_labels,validate_port_check_labels
from source_evidence_binding import bind_named_sources
r=Path.cwd();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());source='9b49efba1e44faf3d2dd4d31e123e874e2434ad1';core='4217e14083c6ecac116216e08d57f4361eb2f12d';verifier='0cb35c8d1c251656c7045dd462904f99567dd3eb'
pub=Path('evidence/01_PT/015_NK-WEB-001/evidence/PG21064-login-failure-http-six-v1');m=load(pub/'manifest.json');assert sha(pub/'manifest.json')=='f691b66f59494be9108aa42ebdae4c58b0cbe405ab135f470cf4e8c5cf2a9223';projection=project_port(m,dict(source=source,tests=6,physical=1,four=[33,2,1,8]));assert m['productionCoreMain']==core
for name,h in m['files'].items():assert '/' not in name and sha(pub/name)==h
names=['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/MqLoginFailureHandler.java','src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/MqLoginFailurePortTest.java'];bind_named_sources(r,m['inputHashes'],names,names)
for name in names:assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+name])).hexdigest()==m['inputHashes'][name]
slot=Path(m['originalManifest']['path']).parent;raw=load(slot/'manifest.safe.json');assert sha(slot/'manifest.safe.json')==m['originalManifest']['sha256'] and raw['actualExit']==0 and raw['begin']['source']==source
for stage in raw['stages'].values():assert stage['actualExit']==0 and not stage['timedOut']
for key,pinned in [('producerGitArtifact',source),('verifierGitArtifact',verifier)]:
 item=m[key];assert item['source']==pinned and hashlib.sha256(subprocess.check_output(['git','show',pinned+':'+item['path']])).hexdigest()==item['sha256']
assert raw['begin']['driverSha256']==m['producerGitArtifact']['sha256'];cfg=Path('evidence/01_PT/018_NK-OPS-001/input/097_login_failure_http.json');assert hashlib.sha256(json.dumps(load(cfg),sort_keys=True).encode()).hexdigest()==raw['begin']['configHash']==m['configHash'] and hashlib.sha256(subprocess.check_output(['git','show',source+':'+str(cfg)])).hexdigest()==sha(cfg)
actual=[];environment=[]
for p in sorted((slot/'xml').glob('TEST-*.xml')):
 tree=E.parse(p).getroot();assert all(int(tree.get(k,'0'))==0 for k in ['failures','errors','skipped']);assert not tree.findall('.//failure') and not tree.findall('.//error') and not tree.findall('.//skipped')
 for c in tree.findall('testcase'):actual.append((c.get('classname'),c.get('name').removesuffix('()')))
 props={x.get('name'):x.get('value') for x in tree.findall('properties/property')};assert props['java.io.tmpdir']==str(slot/'tmp');environment.append({k:props.get(k) for k in ['os.name','os.arch','os.version','java.version','java.vendor']})
assert sorted(actual)==sorted(map(tuple,m['selectedTestMethods'])) and len(actual)==len(set(actual))==6
spec=Path('evidence/01_PT/015_NK-WEB-001/060_Login失敗自己所有HTTP境界単体仕様.md').read_text();pairs=re.findall(r'\|(PT-LOGIN-FAIL\d{3})\|(\w+)\|',spec);assert len(pairs)==6 and {n for _,n in pairs}=={n for _,n in actual}
coverage={c.get('name'):{x.get('type'):{'covered':int(x.get('covered')),'missed':int(x.get('missed'))} for x in c.findall('counter')} for c in E.parse(slot/'coverage.xml').getroot().findall('.//package/class')};assert coverage==m['coverage']
normal=load(r.parent/'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json');assert normal['source']==core and normal['actualExit']==0
for n,h in normal['begin']['inputHashes'].items():assert sha(n)==h
web=normal['jars']['web'];assert sha(web['path'])==web['sha256']
with zipfile.ZipFile(web['path']) as z:
 for n,h in m['physicalHashes'].items():assert hashlib.sha256(z.read(n+'.class')).hexdigest()==h
ex=(slot/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "'+m['session']+'"' in ex
for n,crc in m['physicalClassIds'].items():assert re.search(r'^'+crc+r'\s+\d+ of\s+\d+\s+'+re.escape(n)+r'$',ex,re.M)
review=m['jdkExceptionInitializationReview'];assert review['source']==verifier and review['testsReexecuted']==0 and sha(review['path'])==review['sha256'];sdk=load(review['path']);assert sdk['decision']=='STATIC_JDK_CONSOLE_JDBC_CONVERTER_METADATA_CLOSURE' and sdk['source']==source and sdk['originalRun']=='PG21064' and sdk['originalManifestSha256']==m['originalManifest']['sha256'];assert sdk['consoleSha256']=='3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892' and all(not v for v in sdk['classpathDriverProviderEntries'].values())
static=Path('evidence/01_PT/015_NK-WEB-001/evidence/PG21062-login-failure-style-static-v1/manifest.json');s=load(static);assert s['pmdRaw']==4 and s['applicableViolations']==s['checkstyle']==s['processingErrors']==0 and s['inputHashes']==m['inputHashes'];assert all(not v['applicable'] and v['reason'] for v in s['classification'])
seed=load(r.parent/'PMO/hourly-monitor/completion-execution-kit-20261102/evidence/remaining-work-seed.json');rows=[x for x in seed['sourceEvidenceRows'] if x['path']==names[0]];assert len(rows)==1 and rows[0]['evidenceStatus']=='NOT_IN_CURRENT_MEASUREMENT_REGISTRY'
checks=port_check_labels(projection,s['pmdRaw']);validate_port_check_labels(projection,s['pmdRaw'],checks)
out=Path('evidence/01_PT/015_NK-WEB-001/evidence/PG21078-login-failure-independent-post-v1');assert not out.exists();out.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=source,productionCoreMain=core,verifierSource=verifier,originalPost=dict(path=str(pub/'manifest.json'),sha256=sha(pub/'manifest.json')),tests=6,projection=projection,sourceTestIds=pairs,checks=checks,staticPost=dict(path=str(static),sha256=sha(static)),sdkReview=review,environment=environment,productTestsReexecuted=0,checkerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),checkerSha256=sha(__file__),original282Member=True,actualAuthenticationOrHttpServer=False,formalUpdated=False,newAcceptance=0,effortRate=None);(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=6,testsReexecuted=0,manifestSha256=sha(out/'manifest.json'))))
