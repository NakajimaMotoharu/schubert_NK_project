"""Full protocol changed-test preflight using pinned previous whole120 scope; no tests executed."""
from pathlib import Path
import datetime,hashlib,json,re,zipfile
R=Path.cwd();B=R/'evidence/01_PT/002_NK-PRO-002';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/028_protocol_named59_scope.json');cm=load(RUNS/cfg['compileSlot']/'manifest.json');sm=load(RUNS/cfg['staticSlot']/'manifest.json');O=R/cfg['preflightManifest'];assert not O.parent.exists();assert cm['actualExit']==0 and cm['inputHashes']==sm['inputHashes']
for n,h in cm['inputHashes'].items():assert sha(R/n)==h
old=R/cfg['unchangedOriginal124Manifest'];assert sha(old)=='d2bd415f1fce8d1ae5521aaa89e9fd14838248275537741080619a233df8b678';oldm=load(old);oldpf=load(old.parent/'preflight-manifest.json');assert sha(old.parent/'preflight-manifest.json')==oldm['files']['preflight-manifest.json'] and oldpf['actualExit']==0
oldTests={n:h for n,h in oldpf['inputHashes'].items() if '/src/test/' in n};helper=cfg['changedTestHelperPath'];current=(R/helper).read_text();beginMarker='      // PT-PRO-001-NAMED-RANGE-001-BEGIN\n';endMarker='      // PT-PRO-001-NAMED-RANGE-001-END\n';a=current.index(beginMarker);z=current.index(endMarker)+len(endMarker);block=current[a:z];flagA=current.index('      // PT-PRO-001-NAMED-FLAG-001-BEGIN\n');flagMarker='      // PT-PRO-001-NAMED-FLAG-001-END\n';flagZ=current.index(flagMarker)+len(flagMarker);flagBlock=current[flagA:flagZ];inverse=(current[:a]+current[z:]).replace('import java.math.BigInteger;\n','',1).replace('  private static final int ACCEPTED_NUMERIC_BOUNDARY_VECTORS = 2;\n','',1).replace(flagBlock,'',1);assert hashlib.sha256(inverse.encode()).hexdigest()==oldTests[helper]
assert all(sha(R/n)==h for n,h in oldTests.items() if n!=helper)
discovered={str(p.relative_to(R)) for p in (R/'src/schubert-nk-protocol/src/test/java').rglob('*.java')};assert discovered==set(cfg['testSources']) and len(discovered)==26;assert discovered=={n for n in oldTests if n.endswith('.java')}
cases={};text={}
for n in cfg['testSources']:
 t=(R/n).read_text();text[Path(n).stem]=t;names=re.findall(cfg['declarationRegex'],t);assert len(names)==t.count('@Test')
 if n in cfg['testClasses']:assert names;cases[cfg['testClasses'][n]]=names
 else:assert Path(n).name=='IndependentNamedFieldOracle.java' and not names
 for imp in re.findall(r'^import (?:static )?([^;]+);',t,re.M):assert imp.startswith(('dev.codex.schubert.nk.protocol.','java.','org.junit.'))
 for term in ['@Disabled','@ParameterizedTest','ProcessBuilder','Runtime.getRuntime','java.sql','jakarta.jms','java.net','Files.','@TempDir','Thread.sleep']:assert term not in t
oldcases={(c,n) for c,ns in oldpf['cases'].items() for n in ns};newcases={(c,n) for c,ns in cases.items() for n in ns};assert len(oldcases)==124 and len(newcases)==124 and oldcases==newcases
expectedNames={'zeroAndMaximumAreAcceptedAtEverySupportedWidth','negativeAndFirstOverflowAreRejectedAtEverySupportedWidth','unsupportedWidthsAreRejectedBeforeNumericRangeEvaluation','nullNameIsRejectedBeforeWidthAndValueValidation'};assert set(cases['dev.codex.schubert.nk.protocol.layout.TypedUnsignedRangeBoundaryTest'])==expectedNames
t=text['TypedUnsignedRangeBoundaryTest'];assert t.count('BigInteger.TEN.pow(width)')==2 and 'maximumForDigits' not in t and 'digits <= 18' in t and 'Long.MIN_VALUE, Long.MAX_VALUE' in t and 'Integer.MIN_VALUE, 0, 19, Integer.MAX_VALUE' in t and '"name", failure.getMessage()' in t
assert set(cfg['resources'])=={str(p.relative_to(R)) for p in (R/'src/schubert-nk-protocol/src/test/resources/protocol').glob('*.tsv')} and len(cfg['resources'])==5
for n in cfg['resources']:assert sha(R/n)==oldpf['resources'][n]==sha(RUNS/cfg['compileSlot']/'resources'/n.split('/src/test/resources/')[1])
normal=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22106-api-stop-static-independent-input-v1/normal.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['actualExit']==0 and nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5';assert len(cfg['mainPaths'])==165 and all(sha(R/n)==nm['begin']['inputHashes'][n] for n in cfg['mainPaths']);assert set(cm['dependencies'])=={nm['jars']['protocol']['path'],str(R.parent/'toolchain/m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar')}
for n,h in cm['dependencies'].items():assert sha(Path(n))==h
indexPath=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';assert sha(indexPath)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723';ix=load(indexPath)
with zipfile.ZipFile(nm['jars']['protocol']['path']) as z:
 names=z.namelist();assert not any(h in n for n in names for h in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
 physical={n[:-6] for n in names if n.endswith('.class')};assert physical==set(cfg['targetPhysical'])==set(cfg['currentMainPhysical']) and len(physical)==176
 for n in physical:assert hashlib.sha256(z.read(n+'.class')).hexdigest()==ix[n]['sha256']==cfg['currentMainPhysical'][n]
noCode=[n for n in physical if not ix[n]['hasCode']];assert len(noCode)==13
# Current source inverse is exact; map only the known import/block insertions to raw line coordinates.
items=sm['reports']['pmd']['items'];oldReview=oldpf['pmdApplicability'];rebound=[];importLine=current[:current.index('import java.math.BigInteger;')].count('\n')+1;blockLine=current[:a].count('\n')+1;blockLines=block.count('\n')+flagBlock.count('\n');constantLine=current[:current.index('  private static final int ACCEPTED_NUMERIC_BOUNDARY_VECTORS = 2;')].count('\n')+1
def new_line(oldline):
 value=int(oldline)
 if value>=importLine:value+=1
 if value>=constantLine:value+=1
 if value>=blockLine:value+=blockLines
 return str(value)
for r in oldReview:
 finding=dict(r['finding'])
 if finding['class']=='IndependentNamedFieldOracle':
  for key in ['beginline','endline']:finding[key]=new_line(finding[key])
 line=text[finding['class']].splitlines()[int(finding['beginline'])-1];assert hashlib.sha256(line.encode()).hexdigest()==r['lineTextSha256'];rebound.append(dict(r,finding=finding))
extra=[x for x in items if x['class']=='IndependentNamedFieldOracle' and x['method']=='verifyType' and x['rule']=='UseConcurrentHashMap' and x.get('variable')=='flagFields'];assert len(extra)==1
line=text['IndependentNamedFieldOracle'].splitlines()[int(extra[0]['beginline'])-1];assert 'flagFields = new LinkedHashMap<>(input)' in line and line in flagBlock
rebound.append(dict(finding=extra[0],lineTextSha256=hashlib.sha256(line.encode()).hexdigest(),applicable=False,reason='Invocation-local ordered expected map for one boolean field. Synchronous public constructor/getter reflection; immutable FieldValueSet copy; no shared state or J2EE container.'))
assert sorted(json.dumps(x,sort_keys=True) for x in items)==sorted(json.dumps(x['finding'],sort_keys=True) for x in rebound)
assert len(items)==18 and not sm['reports']['pmd']['processingErrors'] and not sm['reports']['checkstyle']['items'];assert sm['stages']['pmd']['actualExit']==4 and sm['stages']['checkstyle']['actualExit']==0
# Independent canonical field fixture: 59 primitive numeric bindings, not IDs or N17 timestamps.
def fixture(name):return [line.split('\t') for line in (R/'src/schubert-nk-protocol/src/test/resources/protocol'/name).read_text().splitlines() if line and not line.startswith('#')]
areas={}
for row in fixture('fields-ui234-236.tsv'):
 if row[6]!='F':areas.setdefault((row[0],row[1]),[]).append(row)
shapes={}
for row in fixture('named-types-ss323.tsv'):
 for index,area in [(1,'DATA'),(2,'RECORD')]:
  if row[index]!='-':
   values=areas.get((row[0],area),[])
   if row[index] in shapes:assert [(v[2],v[4],v[5],v[6]) for v in shapes[row[index]]]==[(v[2],v[4],v[5],v[6]) for v in values]
   else:shapes[row[index]]=values
ids={'Async job ID','Audio ID','Entry ID','Log ID','Notification ID','Question ID','Script file ID','Speaker ID','User ID'}
numeric=[dict(type=type,field=row[2],width=int(row[4])) for type,rows in shapes.items() for row in rows if row[5]=='N' and int(row[4])!=17 and row[2] not in ids];assert len(numeric)==59 and len(shapes)==69
boolean=[dict(type=type,field=row[2],width=int(row[4])) for type,rows in shapes.items() for row in rows if row[5]=='B'];assert len(boolean)==6 and 'new boolean[] {false, true}' in flagBlock and 'from.invoke(null, new FieldValueSet(flagFields))' in flagBlock and 'getters.get(n).invoke(flagged)' in flagBlock and 'constructor.newInstance(flagArguments)' in flagBlock
assert 'BigInteger.TEN.pow(field.length())' in block and 'boundary < 4' in block and 'boundary < ACCEPTED_NUMERIC_BOUNDARY_VECTORS' in block and 'ACCEPTED_NUMERIC_BOUNDARY_VECTORS = 2;' in current and 'case 0 -> 0' in block and 'case 1 -> maximum' in block and 'case 2 -> -1' in block and 'default -> maximum + 1' in block and 'constructor.newInstance(numericArguments)' in block and 'getters.get(n).invoke(bounded)' in block
O.parent.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=cm['inputHashes'],compileManifestSha256=sha(RUNS/cfg['compileSlot']/'manifest.json'),staticManifestSha256=sha(RUNS/cfg['staticSlot']/'manifest.json'),cases=cases,expectedTests=124,wholeFixtures=25,testSources=26,mainSources=165,physicalClasses=176,noCodeClasses=sorted(noCode),packageAnnotations=7,abstractInterfaces=6,resources={n:sha(R/n) for n in cfg['resources']},dependencies=cm['dependencies'],pmdRawFindings=18,pmdApplicability=rebound,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,original124JUnitMethodsPreserved=True,unchanged25TestSourcesPlusExactHelperExtension=True,helperInverseExact=True,newJUnitMethods=0,retainedIndependentRangeMethods=4,additionalNamedNumericComponents=59,additionalNamedNumericBoundaryObservations=236,numericFixtureBindings=numeric,additionalNamedBooleanComponents=6,additionalNamedBooleanBoundaryObservations=12,booleanFixtureBindings=boolean,suppressionAdded=False,testFixtureExtraction=False,productTestsExecuted=0,heldFourPresentOnClasspath=False,backendOrRootVmNativeOperations=False,oldPreflight=dict(path=str((old.parent/'preflight-manifest.json').relative_to(R)),sha256=sha(old.parent/'preflight-manifest.json')),toolSha256=sha(Path(__file__)))
O.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=124,wholeFixtures=25,staticRaw=18,applicable=0,manifestSha256=sha(O))))
