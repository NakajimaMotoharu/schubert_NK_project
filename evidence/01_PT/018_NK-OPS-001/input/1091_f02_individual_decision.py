"""F02 read-only POM/build/architecture/SYS13 decision; no Maven or runtime re-execution."""
from pathlib import Path
import csv,datetime as dt,hashlib,json,subprocess,xml.etree.ElementTree as X
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';E=B/'evidence';O=E/'PG26048-f02-individual-decision-v1'
P=R.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ns={'m':'http://maven.apache.org/POM/4.0.0'}
source='7aed8eace7c844c2f79f2e39db766faf914890d5'
normal=R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';build=load(normal)
assert type(build['actualExit']) is int and build['actualExit']==0 and build['source']==source and build['testsExecuted'] is False and build['testStatus']=='NOT_RUN_COMPILE_ONLY_NOT_PASS'
assert build['terminal']['actualExit']==0 and build['terminal']['timedOut'] is False and build['begin']['noRootInvocation'] is True
command=build['terminal']['command'];assert '-Dmaven.test.skip=true' in command and command[-1]=='package'
modules=['protocol','storage','bootstrap','api','web','batch'];selected=command[command.index('-pl')+1].split(',');assert selected==['src/schubert-nk-'+n for n in modules]
assert sha(Path(command[0]))==build['begin']['mavenSha256']
table=P/'F02の最初の未受入項目で確認する7つのPOM.tsv';assert sha(table)=='02b0cf22109f0d245063640345f822c57a4969665fd66287bedd8fd85c0c9c26'
rows=list(csv.DictReader(table.open(encoding='utf-8-sig'),delimiter='\t'));assert len(rows)==7
poms={}
for row in rows:
 for key,blobkey in [('ルートpom','Git blob'),('メンバーpom','Git blob（メンバー）')]:
  p=row[key];blob=subprocess.check_output(['git','rev-parse','HEAD:'+p],text=True).strip();assert blob==row[blobkey]
  assert (R/p).read_bytes()==subprocess.check_output(['git','show',source+':'+p])
  selectedInRun=p in build['begin']['inputHashes']
  if selectedInRun:assert sha(R/p)==build['begin']['inputHashes'][p]
  poms[p]=dict(sha256=sha(R/p),gitBlob=blob,recordedInOriginalCompileInputs=selectedInRun)
assert len(poms)==8 # root + seven members, six Production plus one comparison tool.
root=X.parse(R/'pom.xml').getroot();members=[n.text for n in root.findall('m:modules/m:module',ns)];assert members==['program/characterization',*selected]
assert root.findtext('m:properties/m:maven.compiler.release',namespaces=ns)=='25'
assert root.findtext('.//m:requireMavenVersion/m:version',namespaces=ns)=='[3.9.12,4)' and root.find('.//m:dependencyConvergence',ns) is not None
allowed={'protocol':set(),'storage':set(),'bootstrap':{'storage'},'api':{'protocol','storage','bootstrap'},'web':{'protocol','storage','bootstrap'},'batch':{'protocol','storage','bootstrap'}};edges={};testEdges={}
testAllowed={'protocol':set(),'storage':set(),'bootstrap':set(),'api':{'bootstrap'},'web':{'bootstrap','api'},'batch':{'bootstrap'}}
def classify_edges(name,dependencies):
 production=set();testing=set()
 for artifact,scope in dependencies:
  assert scope in ['compile','runtime','test','provided']
  (testing if scope=='test' else production).add(artifact)
 assert production<=allowed[name] and testing<=testAllowed[name]
 return sorted(production),sorted(testing)
assert classify_edges('web',[('api','test')])==([],['api'])
roleNegativeChecks=0
for name,deps in [('web',[('api','compile')]),('bootstrap',[('api','test')]),('web',[('api','unknown')])]:
 try:classify_edges(name,deps)
 except AssertionError:roleNegativeChecks+=1
 else:raise AssertionError('invalid dependency role accepted')
for name in modules:
 tree=X.parse(R/('src/schubert-nk-'+name+'/pom.xml')).getroot()
 internal=[(n.findtext('m:artifactId',namespaces=ns).removeprefix('schubert-nk-'),n.findtext('m:scope',default='compile',namespaces=ns)) for n in tree.findall('m:dependencies/m:dependency',ns) if (n.findtext('m:artifactId',namespaces=ns) or '').startswith('schubert-nk-')]
 edges[name],testEdges[name]=classify_edges(name,internal)
arch=E/'PG22126-current7aed-lineage-quality-independent-v1/manifest.json';assert sha(arch)=='b8afadf6f5069ecdeaabd28cc7ea1cfa9a8ede51ebd904c7f013a70bc562062a';a=load(arch)
assert a['actualExit']==0 and a['productionMainSource']==source and a['physicalClasses']==1845 and all(v==0 for v in a['rules'].values())
assert a['productInitializations']==a['productTestsExecuted']==0 and a['wholeF02Accepted'] is False
for ref in [a['original'],a['currentLineage']]:assert sha(R/ref['path'])==ref['sha256']
inv=load(R/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json');master=load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json');f=next(v for v in master['tasks'] if v['id']=='WBS-F02');assert f['acceptance']['status']=='NOT_ACCEPTED'
requirements=[]
limits={
 'SYS-001':('Existing name/display implementation; final current-source CHR-A01 still separate.','G10/CHR-A01'),
 'SYS-002':('Java25 POM and existing six-module compile0; Ubuntu stock JDK deployment/runtime not newly authenticated.','N01/N02/runtime HOLD'),
 'SYS-003':('Ubuntu26.04 target fixed by approved design; no guest OS or boot ownership query.','N01/N02/VM HOLD'),
 'SYS-004':('PostgreSQL18 design/pinned driver only; current server minor/DDL/connection not authenticated.','N03/DB HOLD'),
 'SYS-005':('Declared internal module edges and existing1845-class architecture rules0; actual JMS routes not newly executed.','P005/P006/N04 dynamic HOLD'),
 'SYS-006':('Approved DIF/current UI evidence referenced, no final same-source browser/CHR acceptance.','G10/CHR-A01'),
 'SYS-007':('Internal boundary rules preserved; final compatibility and operational ownership incomplete.','G10/CHR-L01/QA051 final HOLD'),
 'SYS-008':('On-premise single-site target is design scope; no production/LAN topology action.','C01/C02/N01..N05'),
 'SYS-009':('Native six-module packaging and seven-member reactor, no container prerequisite introduced.','C02/N01 deployment evidence still separate'),
 'SYS-010':('Storage/local-filesystem contract stays in storage/file adapters; no actual master/Backup access.','P003/P019/N03 local-original HOLD'),
 'SYS-012':('Approved global IP/55160 entry policy referenced; actual public connectivity not probed.','C01/C02/N05 HOLD'),
 'SYS-013':('Approved Caddy internal TLS policy referenced; no certificate/private-key/service action.','C01/N05 HOLD'),
 'SYS-014':('Entry configuration separation required; final swap/config contract and runtime verification separate.','C01/N05/IT-ST handoff')}
assert set(limits)==set(f['requirementIds'])
for r in inv['requirements']:
 if r['id'] in limits:
  assert r['requirement'] in (R/r['source']).read_text().splitlines()[r['line']-1]
  basis,remaining=limits[r['id']];requirements.append(dict(requirementId=r['id'],expected=r['requirement'],source=r['source'],line=r['line'],owner=r['owner'],currentEvidence=basis,remaining=remaining,decision='PARTIAL_NOT_FINAL_REQUIREMENT_ACCEPTANCE'))
assert len(requirements)==13
runtime=load(E/'PG26026-saved-target-independent-v2/manifest.json')['environment'];assert runtime['java.runtime.version'].startswith('25.0.4')
checks=[dict(kind='reuse',status='QUALIFIED_COMPILE_AND_ARCHITECTURE_SUBSET_ONLY',basis='Original source22084 terminal0/testskip recorded; same POM/current Main; architecture22126 static only.'),dict(kind='contract',id='WBS-F02:contract',status='PARTIAL',basis='SYS13 implementation/target/environment split above; external and final-source acceptance missing.'),dict(kind='scope',id='WBS-F02:scope',status='BUILD_DECLARATION_AND_SELECTED_SCOPE_MATCHED',basis='Six Production modules selected; comparison is seventh member and not in original selected build.'),dict(kind='quality',id='WBS-F02:quality',status='NOT_ACCEPTED',basis='Compile-only does not supply full PT/coverage/Spotless six gate/CHR/secret/trace/final-source closure. Existing Root2/held4 and global BUG2596/YKT2296/F03/451 HOLD preserved.')]
assert not O.exists();O.mkdir();out=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain=source,poms=poms,uniquePoms=8,productionModules=modules,comparisonModule='program/characterization',originalSelectedModules=selected,originalCommand=command,originalTerminal=build['terminal'],originalCompile=dict(path=str(normal),sha256=sha(normal),testsExecuted=False,testStatus=build['testStatus']),javaRuntimeEvidence=runtime,mavenVersion='3.9.12',mavenVersionBasis='Pinned original command executable/hash and existing toolchain record; no new mvn invocation',declaredInternalEdges=edges,testOnlyInternalEdges=testEdges,dependencyRoleNegativeChecks=roleNegativeChecks,architecture=dict(path=str(arch.relative_to(R)),sha256=sha(arch),physicalClasses=1845,moduleCounts=a['moduleCounts'],rules=a['rules']),requirements=requirements,criteria=checks,decision='NOT_ACCEPTED',F02Accepted=False,newAcceptance=0,productTestsExecuted=0,newMavenRuns=0,newClassfileParsing=0,actualVmBackendOrHeldOperations=0,formalUpdated=False,effortRate=None,remainingActions=['Existing six-module full-quality gate after its permission/dependency conditions; do not rerun compile merely to confirm.','Individual SYS requirement owner evidence and final candidate runtime/CHR closure.','Comparison build/contracts under P020; do not count six-module package as comparison success.'],toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,uniquePoms=8,productionModules=6,sysRequirements=13,originalCompileReexecuted=False,F02Accepted=False,manifestSha256=sha(O/'manifest.json'))))
