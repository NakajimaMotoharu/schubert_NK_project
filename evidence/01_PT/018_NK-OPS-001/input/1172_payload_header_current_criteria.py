"""Canonical independent golden recalculation and same-run two-owner criteria. No JVM or backend."""
from pathlib import Path
import collections,datetime,hashlib,json,re,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26258-payload-header-current-criteria-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();dig=lambda b:hashlib.sha256(b).hexdigest()
full=R/'evidence/01_PT/002_NK-PRO-002/evidence/PG26242-protocol-named59-flag6-independent-v1/manifest.json';assert sha(full)=='62e8f43d53371f2170b713e2cfb1a377d3b1d4e2237bae13aac82d9d4b3d9488';m=load(full);assert m['actualExit']==0 and m['tests']==124 and m['measuredFour100'] and m['heldFourInitializations']==0 and not m['oldExecUnion'];assert all(m[k]==0 for k in ['failures','errors','skipped','aborted'])
dep=B/'evidence/PG26254-header-field-independent-v1/manifest.json';assert sha(dep)=='6c1c4cab4b794126af401de1b3e708141adc6acbc2b6d7e48a4f3abe0b0d907e';dm=load(dep);assert dm['source']==m['source'] and dm['run']==m['singleSession'] and dm['ownerCriteriaVerified']==9
for n in ['coverage.xml','testcases.safe.xml']:assert sha(full.parent/n)==m['files'][n]
xml={x.get('name'):x for x in E.parse(full.parent/'coverage.xml').findall('.//class')};cases=[x.attrib for x in E.parse(full.parent/'testcases.safe.xml').findall('testcase')];names={(x['classname'].rsplit('.',1)[-1],x['name'].removesuffix('()')) for x in cases}
master=load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json');tasks={x['id']:x for x in master['tasks']};inv=load(B/'evidence/PG23972-current-main-method-delta42-v1/class-method-inventory.json');scopes=[];sourceRows=[];filters=[]
for owner in ['WBS-P002-02','WBS-P002-03']:
 task=tasks[owner];paths=set(task['ownedArtifacts']);rows=[x for x in inv if x['sourcePath'] in paths];assert {x['sourcePath'] for x in rows}==paths;counts=collections.defaultdict(lambda:dict(covered=0,missed=0));nc=[];before=len(filters)
 for row in rows:
  p=R/row['sourcePath'];assert sha(p)==row['sourceSha256'];name=row['physicalKey'].split(':',1)[1].removesuffix('.class');node=xml.get(name);assert row['structure'] is not None
  official={(v.get('name'),v.get('desc')) for v in node.findall('method')} if node is not None else set();c={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in node.findall('counter')} if node is not None else {};text=p.read_text();leaf=name.rsplit('/',1)[-1].rsplit('$',1)[-1]
  for k,v in c.items():counts[k]['covered']+=v['covered'];counts[k]['missed']+=v['missed']
  for q in row['structure']['methods']:
   n=q['name'];d=q['descriptor']
   if not q['hasCode'] or (n,d) in official:continue
   if name.endswith('$1') and n=='<clinit>':reason='JAVAC_SWITCHMAP_STANDARD_FILTER'
   elif re.search(r'\brecord\s+'+re.escape(leaf)+r'\b',text) and (n in ['hashCode','equals','toString'] or d.startswith('()')):reason='JAVAC_RECORD_STANDARD_FILTER'
   elif re.search(r'\benum\s+'+re.escape(leaf)+r'\b',text) and n in ['values','valueOf','$values','<init>']:reason='JAVAC_ENUM_STANDARD_FILTER'
   elif n=='<init>' and d=='()V' and re.search(r'private\s+'+re.escape(leaf)+r'\(\)\s*\{\s*\}',text):reason='PRIVATE_EMPTY_UTILITY_CTOR_STANDARD_FILTER'
   else:raise AssertionError((name,n,d))
   filters.append(dict(owner=owner,source=row['sourcePath'],className=name,method=n,descriptor=d,reason=reason,measuredRuntimeCoverageClaimed=False))
  if not any(q['hasCode'] for q in row['structure']['methods']):nc.append(name)
  sourceRows.append(dict(owner=owner,path=row['sourcePath'],sourceSha256=row['sourceSha256'],physicalClass=name,physicalClassSha256=row['classSha256'],coverage=c))
 assert all(counts[k]['covered']>0 and counts[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH']);assert task['dependencies']==['WBS-P001-01','WBS-P001-02'];assert task['acceptance']['source']=='7fffab57a567914956b66452e5e54388642efdec'
 scopes.append(dict(owner=owner,sourceArtifacts=len(paths),physicalClasses=len(rows),coverage=dict(counts),measuredOwnerFour100=True,defaultFilters=len(filters)-before,noCodeClasses=nc,dependencies=task['dependencies'],dependenciesCurrentSameSourceRunVerified=True,sharedClassReferences=task['sharedClassReferences'],wholeNativeOrBrokerNotClaimed=True))
# Independent expected buffers from canonical field tables already compared to origin/main, never production methods.
prior=B/'evidence/PG26248-canonical-ui-field-comparison-v1';cm=load(prior/'manifest.json');cp=B/'evidence/PG26250-header-layout-field-current-criteria-v1';assert load(cp/'manifest.json')['canonicalPhysicalFieldRows']==389
fields={(s['layout'],s['area']):[v['tuple'] for v in s['canonicalFields']] for s in load(prior/'scope-comparison.json')};layouts=load(cp/'canonical64-layouts.json');fixture=R/'src/schubert-nk-protocol/src/test/resources/protocol/payload-golden-ui234-236.tsv';golden={v[0]:v[1:] for l in fixture.read_text().splitlines() if l and not l.startswith('#') for v in [l.split('\t')]};assert len(golden)==64
vectors=[]
def independent_bytes(layout,area,length,profile):
 out=bytearray(b' '*length)
 for name,start,width,wire,presence,rule in fields.get((layout,area),[]):
  at=int(start)-1;width=int(width)
  if presence=='F':value=b' '*width
  elif profile=='error':value=(b'0' if wire=='N' else b' ')*width
  elif name=='Log type' and at==17:value=b'REQUEST'.ljust(width,b' ')
  elif profile=='min' and presence!='M':value=b' '*width
  elif wire=='N':value=(b'9' if profile=='max' else b'0')*width
  elif wire=='B':value=b'1' if profile=='max' else b'0'
  else:value=b'Z'*width if profile=='max' else b'A'.ljust(width,b' ')
  assert len(value)==width;out[at:at+width]=value
 return bytes(out)
for row in layouts:
 layout,kind,interaction,dataLength,recordLength,count,total=row;expected=[]
 for area,size,profile in [('DATA',int(dataLength),'min'),('DATA',int(dataLength),'max'),('RECORD',int(recordLength),'min'),('RECORD',int(recordLength),'max')]:
  h=dig(independent_bytes(layout,area,size,profile));expected.append(h);vectors.append(dict(layout=layout,area=area,profile=profile,expectedSha256=h,fixtureSha256=golden[layout][len(expected)-1],basis='Canonical UI byte offsets/length/type/presence plus independently stated ASCII boundary rule, not production codec or helper'))
 expected.append(dig(independent_bytes(layout,'DATA',int(dataLength),'error')) if kind=='S' else '-')
 if kind=='S':vectors.append(dict(layout=layout,area='DATA',profile='generic-error',expectedSha256=expected[-1],fixtureSha256=golden[layout][-1],basis='All N ASCII zero and X/B space; result-specific Login/Cancel overrides checked independently in their explicit normal cases'))
 assert expected==golden[layout],layout
assert len(vectors)==287 and all(x['expectedSha256']==x['fixtureSha256'] for x in vectors)
# Behaviour-specific independent assertions, not only roundtrip or coverage.
checks=[
 ('PT-PRO-002-P07','PayloadGoldenVectorTest','allSixtyFourLayoutsMatchIndependentMinimumMaximumAndErrorHashes','64 canonical min/max data/record and31 generic error fixed hash oracles; these are low-level codec bounds, not semantically valid business messages.'),
 ('PT-PRO-002-P08','PayloadGoldenVectorTest','everyRepeatingLayoutAcceptsItsMaximumRecordBoundary','14 layouts max records/total from independent UI233 limits, not SUT-derived expected.'),
 ('PT-PRO-002-P09','PayloadGoldenVectorTest','sharedCodecProducesIdenticalBytesUnderConcurrentUse','Eight threads, literal384 bytes, latch/get/termination bounded10s and finally shutdown; no mutable singleton state.'),
 ('PT-PRO-002-P03','PayloadCodecTest','encodeRejectsUnknownMissingWrongTypeAndRecordViolations','Fixed/unknown field, missing/wrongkind, record count/null rejects before wire result.'),
 ('PT-PRO-002-M02','PayloadCodecTest','decodeRejectsLengthsNullsFixedValuesAndBadErrorFillers','Exact declared lengths, null references/elements, fixed/reserved/error filler corruption reject typed errors.'),
 ('PT-CODEC-AUTHERR-001','AuthenticationErrorProfileTest','loginLockAndFailurePreserveOnlyApprovedErrorFields','432 literalbytes; retry offsets167/6, locked0/1/900; usermessage176/256; success-only data spaces, count0.'),
 ('PT-CODEC-AUTHERR-002','AuthenticationErrorProfileTest','malformedLoginErrorBoundariesAndTypesAreRejected','Retry901/negative/wrongkind/missing; message256/257bytes/control/null; forbidden fields and filler mismatch.'),
 ('PT-CODEC-AUTHERR-003','AuthenticationErrorProfileTest','allOtherResponseErrorProfilesRetainTheirIndividualContracts','31 response layouts/error codes, Login onlytwofield/Cancel0107state only, other29 blank/zero records0.'),
 ('PT-PRO-002-E02','PayloadCodecTest','resultCodeProfilePreservesOnlyTheApprovedCancellationConflictState','NTC0107 exactly PROCESSING/COMPLETED/ERROR and unset cancel time; rejected unknown/omitted/wrongtype.'),
 ('PT-PRO-002-H01','MessageCodecTest','headerEncodingMatchesIndependentUi232GoldenVector','Literal256byte header positional expected, fixed magic/version/QS/JST/UUID/rootrelation/length/reserved.'),
 ('PT-PRO-002-H01-RSP-EVT','MessageCodecTest','responseAndEventHeadersRoundTripWithoutLeakingContext','Independent literal256 response andevent expected, context64 vs spaces, IDs/result andtotal.'),
 ('PT-PRO-002-H02','MessageCodecTest','headerDecoderRejectsEveryFixedFieldAndProfileCorruption','Single-field byte corruption, versions/reserved/result/context/IDs/declaredformula typedrejection.'),
 ('PT-PRO-002-T01','MessageCodecTest','transportAndRouteContractsRejectEveryMismatch','Pure transport metadata Bytes/persistent2/protocol001/IDs/layout/correlation/dest/reply/expiry exact; null and onefault mismatch; no actual JMS object/provider.'),
 ('PT-PRO-002-TNULL','MessageCodecTest','metadataAndExpectedRouteEstablishNullAndRangeContracts','Metadata/route null andrange contracts at immutable construction; no connected broker/client.'),
 ('PT-PRO-002-M01','MessageCodecTest','fullMessageRoundTripsAtByteBoundariesAndRejectsInvalidSizes','Exact encodedbody bounds, overflow/short/oversize/length mismatch before any business dispatch.')]
matrix=[]
for tid,cl,case,expected in checks:
 assert (cl,case) in names
 matrix.append(dict(testId=tid,case=cl+'#'+case,independentExpected=expected,actual='PASSED_IN_SAME_NORMAL124_PINNED_RUN',rawPerVectorCaptureClaimed=False))
semanticCases=[x for x in cases if x['classname'].endswith('.PayloadSemanticValidatorTest')];assert len(semanticCases)>=6
for x in semanticCases:matrix.append(dict(testId='PT-PRO-002-P06/'+x['name'].removesuffix('()'),case=x['classname']+'#'+x['name'],independentExpected='Explicit valid literal field fixtures and one-condition invalid mutations of UI234236/SS322§9; original authored assertions retained, no database business-state claim.',actual='PASSED_IN_SAME_NORMAL124_PINNED_RUN',rawPerVectorCaptureClaimed=False))
criteria=[dict(id=x['owner']+':'+k,status='VERIFIED_CURRENT_HOST_PROTOCOL_COMPONENT',evidence={'contract':['individual-oracle-matrix.json','independent287-fixed-golden-hashes.json'],'scope':['source-physical-counters.json','owner-scopes.json'],'quality':[str(full.relative_to(R)),'default-filter-review.json']}[k],global451OrActualBrokerNativeAccepted=False) for x in scopes for k in ['contract','scope','quality']]
O.mkdir();files={'owner-scopes.json':scopes,'source-physical-counters.json':sourceRows,'default-filter-review.json':filters,'independent287-fixed-golden-hashes.json':vectors,'individual-oracle-matrix.json':matrix,'individual-criteria.json':criteria}
for name,value in files.items():(O/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],run=m['singleSession'],outcome='TWO_CURRENT_HOST_OWNERS_SIX_CRITERIA_VERIFIED_NO_FORMAL_OR_NEW_ORIGINAL_LEAF',ownerIds=[x['owner'] for x in scopes],criteriaVerified=6,criteriaTotal=6,ownerSummaries=scopes,canonicalGoldenHashComparisons=287,oracleMatrixCases=len(matrix),sameSourceRunManifest=dict(path=str(full.relative_to(R)),sha256=sha(full)),sameSourceDependencyProof=dict(path=str(dep.relative_to(R)),sha256=sha(dep)),productTestsReexecuted=0,fixtureOrProductionModified=False,newOriginal190Acceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files={n:sha(O/n) for n in files},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,criteria=6,hashes=287,oracles=len(matrix),scopes=scopes,manifestSha256=sha(O/'manifest.json'))))
