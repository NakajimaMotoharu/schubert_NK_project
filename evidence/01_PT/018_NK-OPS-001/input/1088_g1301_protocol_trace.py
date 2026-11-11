"""G13.01 exhaustive current protocol byte/catalog reference join, never a new PT or owner acceptance."""
from pathlib import Path
import csv,datetime as dt,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';E=B/'evidence';O=E/'PG26044-g1301-protocol-trace-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
p=E/'PG24854-protocol-all165-method742-reference-join-v1/manifest.json';assert sha(p)=='95dfcd317533336e16bd87f58fb074c6b2610da753b88269cc08d35aef7b1e7a';trace=load(p)
assert trace['actualExit']==0 and trace['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
assert trace['sourceArtifacts']==165 and trace['physicalClasses']==176 and trace['officialMeasuredMethods']==742
assert trace['allSourceAndXmlMethodKeysExactlyOnce'] is True and trace['methodReferencesCompleteOnly'] is True and trace['whole451Accepted'] is False
proofs=[]
for ref in trace['referenceProofs']+[trace['normalProof']]:
 q=R/ref['path'];assert sha(q)==ref['sha256'];v=load(q);assert type(v['actualExit']) is int and v['actualExit']==0
 proofs.append(dict(ref,meaning='EXISTING_REFERENCE_ONLY_NO_REEXECUTION'))
assert len(trace['referenceProofs'])==12
normal=load(R/trace['normalProof']['path']);assert normal['tests']==120 and normal['sourcePrograms']==165 and normal['physicalInputClasses']==176
assert normal['productionCoreMain']==trace['source'] and normal['measuredFour100'] is True and normal['strictMeasuredFour100GateExit']==0 and normal['unclassifiedOfficialFilterCount']==0
assert all(normal[k]==0 for k in ['failures','errors','skipped','aborted'])
inv=load(R/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json');view=inv['currentSourceArtifactStructureView20261108'];ref=view['descriptorBase'];assert sha(R/ref['path'])==ref['sha256']
rows=[v for v in load(R/ref['path']) if v['path'].startswith('src/schubert-nk-protocol/src/main/java/')]
assert len(rows)==165 and len({r['path'] for r in rows})==165
current={}
for row in rows:assert sha(R/row['path'])==row['sha256'];current[row['path']]=dict(sha256=row['sha256'],owner=row['owner'],costOwner=row['costOwner'])
names=set(subprocess.check_output(['git','ls-files','src/schubert-nk-protocol/src/main/java'],text=True).splitlines());assert names==set(current)
cat='documents/200_UI/230_インターフェース/233_固定長電文インターフェース一覧.md';raw=subprocess.check_output(['git','show','origin/main:'+cat]);assert raw==(R/cat).read_bytes()
catalog={}
for line in raw.decode().splitlines():
 cells=[v.strip() for v in line.split('|')]
 if len(cells)<9:continue
 m=re.fullmatch(r'([QSE]) `([A-Z0-9]{8})`',cells[2])
 if m:
  key=m[2];assert key not in catalog;catalog[key]=[m[1],cells[3],*[int(c.replace(',','')) for c in cells[4:8]]]
fixture=R/'src/schubert-nk-protocol/src/test/resources/protocol/layouts-ui233.tsv'
actual={}
for line in fixture.read_text().splitlines():
 if not line or line.startswith('#'):continue
 cells=line.split('\t');assert len(cells)==7 and cells[0] not in actual;actual[cells[0]]=[cells[1],cells[2],*map(int,cells[3:])]
assert len(catalog)==len(actual)==64 and actual==catalog
named=R/'src/schubert-nk-protocol/src/test/resources/protocol/named-types-ss323.tsv';typeIds=[l.split('\t')[0] for l in named.read_text().splitlines() if l and not l.startswith('#')]
assert len(typeIds)==len(set(typeIds))==64 and set(typeIds)==set(catalog)
requirements=[]
for row in inv['requirements']:
 if row['id'] in ['SYS-011','SCP-001','SCP-002','SCP-003','SCP-006']:
  text=(R/row['source']).read_text().splitlines();assert row['requirement'] in text[row['line']-1]
  requirements.append({k:row[k] for k in ['id','source','line','requirement','owner','designTrace']})
assert len(requirements)==5
assert not O.exists();O.mkdir()
gaps=[dict(id='G1301-BRANCH-ORACLE',condition='All individual branch oracles remain unverified by reference links alone; bind each B owner criteria and independent expected input/results.',nextOwner='Existing protocol B individual contracts',additionalBudgetAddedPp=0),dict(id='G1301-CASE-PROBE',condition='115 of120 actual cases referenced in method join; per-case probe attribution null. Normal120 genuinely passed, but no attribution or five extra links invented.',nextOwner='Existing B owner method/oracle review',additionalBudgetAddedPp=0),dict(id='G1301-OWNER-ACCEPTANCE',condition='Current program and registry owner acceptance remains false; same final-source 451/CHR/ending dependencies separate.',nextOwner='Existing B and final G13/G11',additionalBudgetAddedPp=0)]
v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain=trace['source'],referenceProof=dict(path=str(p.relative_to(R)),sha256=sha(p)),existingProofs=proofs,currentSourceBindings=current,sourceArtifacts=165,physicalClasses=176,officialMeasuredMethodReferences=742,layouts=64,layoutCatalog=dict(path=cat,sha256=sha(R/cat)),layoutFixture=dict(path=str(fixture.relative_to(R)),sha256=sha(fixture)),namedFixture=dict(path=str(named.relative_to(R)),sha256=sha(named)),requirements=requirements,layoutTableIndependentAllRowsMatch=True,existingNormalTests=120,newProductTests=0,productTestsExecuted=0,newCompilerRuns=0,newCoverageMeasurements=0,allBranchOraclesIndividuallyVerified=False,perCaseProbeAttribution=None,unclosedConditions=gaps,scope='CURRENT_STATIC_TRACE_AND_MISSING_CONDITIONS_ONLY',G1301WholeAccepted=False,wholeG13Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sourceArtifacts=165,physicalClasses=176,methods=742,layouts=64,unclosedConditions=len(gaps),newTests=0,manifestSha256=sha(O/'manifest.json'))))
