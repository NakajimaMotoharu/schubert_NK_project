"""A3 public proof applicability; never execute a fixture or read actual class/secret/raw data."""
import csv,datetime,hashlib,json,sys
from pathlib import Path
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';E=B/'evidence';start,end,run=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3];assert 1<=start<=end<=12
P=R.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件';plan=P/'全領域で週20件のときの625行WBS.tsv';assert hashlib.sha256(plan.read_bytes()).hexdigest()=='b7bf00dbea8ab47d3820db70335342e543f6f7bcd595e2ffc43e6e1086054579'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());rows=[x for x in csv.DictReader(plan.open(encoding='utf-8-sig'),delimiter='\t') if x['実行ID'] in ['A3-'+str(i).zfill(2) for i in range(start,end+1)]];assert len(rows)==end-start+1
normal=load(E/'PG22106-api-stop-static-independent-input-v1/normal.json');classHashes={}
for key,value in normal['normalPhysicalClassHashes'].items():classHashes.setdefault(key.split(':',1)[1].removesuffix('.class'),[]).append(value)
canon=load(E/'PG26176-six-domain-initial-owner-join-v1/current-owner-and-ending-gaps.json');ownerByPath={p:x['owner'] for x in canon for p in x['sourcePaths']};O=E/(run+'-a3-'+str(start).zfill(2)+'-'+str(end).zfill(2)+'-existing-proof-applicability-v1');assert not O.exists();results=[];cache={}
for row in rows:
 ref=row['出典'];p=R/ref;assert ref.startswith('evidence/01_PT/') and p.name=='manifest.json'
 if ref not in cache:
  m=load(p);assert m['actualExit']==0 and m['productionCoreMain']==normal['source'];checks=[]
  for name,expected in m['inputHashes'].items():
   if Path(name).name in ['RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java']:
    checks.append(dict(path=name,qualification='HELD_TEST_SOURCE_NOT_READ',expectedSha256=expected,actualSha256=None));continue
   assert not Path(name).is_absolute() and '..' not in Path(name).parts and name.startswith(('src/','evidence/01_PT/'))
   assert not name.endswith('.class') and not (R/name).is_symlink()
   actual=sha(R/name);checks.append(dict(path=name,expectedSha256=expected,actualSha256=actual,qualification='CURRENT_BYTES_MATCH' if actual==expected else 'CURRENT_BYTES_DIFFER_UNQUALIFIED'))
  physical=[]
  for name,expected in m['physical'].items():
   values=classHashes.get(name,[]);physical.append(dict(className=name,manifestSha256=expected,currentPublicMetadataSha256=values,qualification='CURRENT_METADATA_MATCH' if len(values)==1 and values[0]==expected else 'CURRENT_METADATA_UNCONFIRMED'))
  cache[ref]=(m,checks,physical)
 m,checks,physical=cache[ref];target=row['作業・成果物'].split(' の')[0];targets=[x for x in checks if '/src/main/java/' in x['path'] and Path(x['path']).name==target+'.java'];assert len(targets)==1
 main=targets[0]['path'];currentOwner=ownerByPath[main]
 remains=['Original proof is limited to declared in-memory port/independent fixture scope, not actual backend/native/VM/Root/session or whole owner acceptance.','Current-source/old-run references are not new execution, new coverage, new Test IDs or 451 completion.','Per-case method/oracle links and original owner ending dependencies still need separate individual acceptance.']
 if target in ['ApiJdbcPool','WebJdbcPool','QuestionWorkListener','WebLogListener','DirectoryCalls']:remains.append('Natural zero BRANCH is N/A with ratio null; aggregate or other-class branch coverage does not convert this source to nonempty four-counter100.')
 if target=='WebServiceMetricBinding':remains.append('Original22 declarations include one excluded actual dependency;21 qualified cases do not make original22 accepted. Preserve notRunDeclaredMethods and wholeOriginal22Accepted=false.')
 if target in ['ServiceDatabaseAdmission','ServiceDatabaseSource']:remains.append('Plan A3 nominal WBS-P019-01 differs from canonical source owner WBS-P018-05. A3 applicability cost stays A3; source manufacturing/normal PT belongs to canonical P018-05, with P019 consumer reference only.')
 results.append(dict(id=row['実行ID'],target=target,planScopeReference=row['範囲参照'],currentSourceOwner=currentOwner,planEstimate={k:float(row[k+'pp']) for k in ['低位','標準','高位']},manifest=dict(path=ref,sha256=sha(p),source=m['source'],productionCoreMain=m['productionCoreMain'],testsInOriginalManifest=m['tests']),inputChecks=checks,physicalChecks=physical,originalCoverage=m['coverage'],originalWholeTargetPredicates={k:v for k,v in m.items() if k.startswith('whole') or k.startswith('branch') or k in ['notRunDeclaredMethods','wholeOriginal22Accepted','newFixtureReplacesHeldBackendTest']},applicability='APPLIES_ONLY_TO_ORIGINAL_LIMITED_SCOPE_UNCHANGED_CURRENT_BYTES' if all(x['qualification']=='CURRENT_BYTES_MATCH' for x in checks) and all(x['qualification']=='CURRENT_METADATA_MATCH' for x in physical) else 'PARTIAL_CURRENT_SOURCE_REQUALIFICATION_REQUIRED',remaining=remains,productTestsExecuted=0,newAcceptance=0))
O.mkdir();(O/'per-item-applicability.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),productionCoreMain=normal['source'],workIds=[x['id'] for x in results],individualApplicabilityDecisions=len(results),limitedScopeApplicable=sum(x['applicability'].startswith('APPLIES_ONLY') for x in results),sourceOrDependencyChangedItems=sum(not x['applicability'].startswith('APPLIES_ONLY') for x in results),uniqueOriginalManifests=len(cache),existingCaseRefsAcrossUniqueManifests=sum(x[0]['tests'] for x in cache.values()),inputHashChecksAcrossUniqueManifests=sum(len(x[1]) for x in cache.values()),physicalMetadataChecksAcrossUniqueManifests=sum(len(x[2]) for x in cache.values()),actualClassFileReads=0,rootTwoTestFileReads=0,productTestsExecuted=0,newTestIds=0,newCoverageMeasurements=0,actualBackendVmRootKeyOperations=0,newAcceptance=0,formalUpdated=False,effortRate=None,files={'per-item-applicability.json':sha(O/'per-item-applicability.json')},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(m,ensure_ascii=False))
