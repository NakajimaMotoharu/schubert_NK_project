"""F03/1 public rule/source inventory only; never opens binaries or held Test bodies."""
from pathlib import Path
import csv,datetime,hashlib,json,subprocess,xml.etree.ElementTree as X
R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p))
load=lambda p:json.loads(p.read_text())
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
start=load(B/'input/2338_f03_stage1_start.json'); source=start['source']; head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
def production_main_paths(names):
 result=[]
 for name in names:
  parts=Path(name).parts
  if len(parts)>=6 and parts[0]=='src' and parts[2:5]==('src','main','java') and name.endswith('.java'):
   result.append(name)
 return sorted(result)
def git_names(args):
 return [n for n in subprocess.check_output(['git',*args],text=True).split('\0') if n]
assert production_main_paths(git_names(['diff','--name-only','-z',source,'--','src']))==[]
assert production_main_paths(git_names(['ls-files','--others','--exclude-standard','-z','--','src']))==[]
for x in start['oracleRefs']+start['configurationInputRefs']:assert sha(R/x['path'])==x['sha256']
ns={'m':'http://maven.apache.org/POM/4.0.0'}; root=X.parse(R/'pom.xml').getroot()
modules=[x.text for x in root.findall('m:modules/m:module',ns)]
production=['src/schubert-nk-'+x for x in ['protocol','storage','bootstrap','api','web','batch']]
assert set(modules)==set(production+['program/characterization']) and len(modules)==7
props={x.tag.split('}')[-1]:x.text for x in root.find('m:properties',ns)}
assert props['maven.compiler.release']=='25' and props['jspecify.version']=='1.0.1'
configs=[]
for p in [R/'pom.xml',*[R/x/'pom.xml' for x in production]]:
 tree=X.parse(p).getroot(); plugins=[]
 for v in tree.findall('.//m:plugin',ns):
  plugins.append(dict(artifact=v.findtext('m:artifactId',namespaces=ns),version=v.findtext('m:version',namespaces=ns),configuration=X.tostring(v,encoding='unicode')))
 configs.append(dict(**ref(p),plugins=plugins))
pmd=R/'tools/quality/static/pmd.xml';cs=R/'tools/quality/static/checkstyle.xml'
assert [v.attrib['ref'] for v in X.parse(pmd).getroot() if v.tag.endswith('rule')]==['category/java/errorprone.xml','category/java/security.xml','category/java/multithreading.xml']
assert not X.parse(pmd).getroot().findall('.//{*}exclude-pattern')
assert not any('Suppress' in v.attrib.get('name','') for v in X.parse(cs).iter())
held={'RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java'}; hashes={}; heldNames=[]; inventory=[]
names=subprocess.check_output(['git','ls-files','--','src/*/src/main/java/*.java','src/*/src/test/java/*.java'],text=True).splitlines()
assert names and len(names)==len(set(names))
for mod in production:
 own=[p for p in names if p.startswith(mod+'/')]; main=[p for p in own if '/src/main/java/' in p]; tests=[p for p in own if '/src/test/java/' in p]
 for name in own:
  if Path(name).name in held:
   heldNames.append(dict(path=name,sha256=None,reason='NAMES_ONLY_HOLD_NO_STAT_HASH_READ_COMPILE'));continue
  assert name.endswith('.java') and '/target/' not in name
  hashes[name]=sha(R/name)
 inventory.append(dict(module=mod,mainJavaSourceFiles=len(main),testJavaNamedFiles=len(tests),testJavaHashedFiles=sum(p in hashes for p in tests),heldTestNames=[p for p in tests if Path(p).name in held],physicalMainClasses=None,wholeCurrentModuleQualityAccepted=False))
assert len(heldNames)==2
output=B/'evidence/PG29526-f03-public-six-module-preparation-v1';output.mkdir()
write(output/'public-java-source-inventory.json',dict(sourceBasis=head,productionCoreMain=source,publicJavaSha256=hashes,heldTestNames=heldNames,physicalMainDenominator=None,binaryReadStatCompileLoadCount=0))
write(output/'root-child-pom-configuration.json',dict(inputs=configs,productionModules=production,toolModuleSeparate='program/characterization',rootProperties=props,rules=[ref(pmd),ref(cs)]))
proofs=[]
for name in ['PG29478-login-independent-v1','PG29382-env-independent-v1','PG29434-attempt-independent-v1']:
 p=B/'evidence'/name/'manifest.json'
 if not p.exists():continue
 v=load(p); assert v['actualExit']==0
 proofs.append(dict(**ref(p),evidenceSource=v.get('source'),scope='LIMITED_COMPONENT_HISTORY_NOT_CURRENT_WHOLE_SIX_MODULE_ACCEPTANCE'))
assert proofs and proofs[0]['path'].endswith('PG29478-login-independent-v1/manifest.json')
missing=[
 dict(id='F03-MISSING01',scope='All six production modules',condition='Fresh same-source compiler/NullAway/lint/SpotBugs physicalClassStats+MissingClass/Error0+format/PMD/Checkstyle applicability all0, independent oracle and no suppression',status='NOT_ACCEPTED',reason='Limited qualified closure cannot prove current whole modules; current physical denominator unverified, historical1643/1843 not reused.'),
 dict(id='F03-MISSING02',scope='Root2 Test bodies and actual4 .class',condition='Existing individual HOLD prerequisites resolved without probing or rerunning denied operations',status='HOLD',reason='Names-only Root tests; TemporaryInfrastructureException/FingerprintKeyRing/ResponseSnapshotCodec/WebStartupException actual binaries never stat/read/hash/compile/load. Public .java source inventory does not authorize them.'),
 dict(id='F03-MISSING03',scope='Root/VM/cohort/DB/broker/native/Browser/Current capture',condition='Existing safety/owner/access/QA051 final gates independently satisfied',status='HOLD',reason='No physical environment operation from public config or old success.'),
 dict(id='F03-MISSING04',scope='F03/2 and451 full acceptance',condition='Individual contract/scope/quality, same-source/run whole PT+four100+CHR/secret/trace+owned termination evidence',status='NOT_ACCEPTED',reason='Zero executed new product tests here; no formal update1964/53; /1 inventory alone never completes /2 or F03.'),
 dict(id='F03-MISSING05',scope='Characterization tool',condition='Whole applicable tool tests and actual gates under separate owner',status='SEPARATE_HOLD',reason='Tool module is seventh reactor entry, not seventh production module. GateCli whole12 actual20GiB and Current capture constraints retained; no fake capacity or extraction.')]
checks=[dict(id='F03-PREP01',expected='Root seven reactor entries partition exactly six production and one characterization tool.',actual='MATCH'),dict(id='F03-PREP02',expected='411/451/SS352354 rule, all six Root/child compiler+analysis config and public source scope fixed by hashes.',actual='MATCH_PUBLIC_INPUTS_NOT_EXECUTED_GATE'),dict(id='F03-PREP03',expected='Historical and selected results do not certify current full physical source or runtime.',actual='SEPARATE_LIMITED_EVIDENCE'),dict(id='F03-PREP04',expected='Residual individual HOLD and missing /2 conditions saved without accessing forbidden bodies/binaries or environment.',actual='MISSING_CONDITIONS_EXPLICIT')]
plan=R.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件/全領域で週20件のときの625行WBS.tsv';row=next(x for x in csv.DictReader(plan.open(encoding='utf-8-sig'),delimiter='\t') if x['実行ID']=='WBS-F03/1'); assert row['標準pp']=='4.0'
manifest=dict(actualExit=0,atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),run='PG29526',source=source,productionCoreMain=source,sourceBasis=head,branch='dev-foundation',endingStatus='ORIGINAL_F03_STAGE1_PUBLIC_SCOPE_AND_MISSING_CONDITIONS_SAVED',completedOriginalPreparationWorkIds=['WBS-F03/1'],rowCriterion=row,wholeEmptyOwnedArtifactAuditClaimed=False,publicInputs=start['oracleRefs']+[ref(R/'documents/300_SS/350_運用・品質/352_Security・credential・監査実装設計.md'),ref(R/'documents/400_PGPT/420_環境/421_開発環境・toolchain構築記録.md')],moduleInventory=inventory,rootAndChildConfiguration=ref(output/'root-child-pom-configuration.json'),sourceInventory=ref(output/'public-java-source-inventory.json'),rules=[ref(pmd),ref(cs)],jspecifyDifference=dict(historical451Initial='1.0.0',currentRoot='1.0.1',authority='421 PG316/SSC098/BUG305 convergence to existing Web1.0.1; historical initial version is not current effective pin.',changed=False),checks=checks,limitedPublicEvidence=proofs,missingConditions=missing,currentPhysicalMainDenominator=None,allSixCurrentStaticQualified=False,newProductTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortCompletionRate=None,actualEnvironmentOperations=0,actual4BinaryOperations=0,root2BodyOperations=0,protected2ToolOperations=0,sourceChanged=False,command='python3 -B evidence/01_PT/018_NK-OPS-001/input/2339_f03_public_quality_inventory.py')
write(output/'manifest.json',manifest)
print(json.dumps(dict(actualExit=0,modules=inventory,publicJavaHashes=len(hashes),heldTestNames=heldNames,manifest=ref(output/'manifest.json')),ensure_ascii=False))
