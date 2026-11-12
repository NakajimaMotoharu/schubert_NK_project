"""Tool checks only: four recorded profiles and negative metadata; no Java/Maven/class/exec access."""
from pathlib import Path
import ast,copy,hashlib,json,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';sys.path.insert(0,str(R/'tools/quality'));import pgpt_closed_host_profile as h
ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n');inventory=ld(R/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json');owners={x['path']:x['owner'] for x in inventory['artifacts']};cases=[];configs=[];O=B/'evidence/PG28190-closed-host-tool-metadata-validation-v1';assert not O.exists();O.mkdir()
examples=[('a-api-config7','PG28080-api-config7-normal-v1','PG28090-api-config7-independent-v1',[7],'4183_API非秘密設定原七単体仕様.md',{'nk.pt.repository':'OWNED_PUBLIC_REPOSITORY'}),('b-router18','PG28102-router18-normal-v1','PG28112-router18-independent-v1',[10,8],'4185_内部エラー振分原十八単体仕様.md',{'spring.security.strategy':'MODE_THREADLOCAL'}),('c-http-metric28','PG28126-http-metric28-normal-v1','PG28136-http-metric28-independent-v1',[10,6,12],'4187_HTTPメトリクス原二十八単体仕様.md',{}),('d-backup-manifest16','PG28156-backup-manifest16-normal-v1','PG28166-backup-manifest16-independent-v1',[8,8,0],'4189_Backup公開manifest原十六単体仕様.md',{})]
for name,prepare,post,totals,spec,props in examples:
 pp=B/'evidence'/prepare/'manifest.json';pm=ld(pp);po=B/'evidence'/post/'manifest.json';m=ld(po);main=pm['apiMainSources'];tests=pm['apiTestSources'];require=lambda ok,msg:h.require(ok,msg);require(len(tests)==len(totals),'known whole source counts');resources=[dict(path=p,placement='TEST_CLASSPATH' if '/src/test/resources/' in p else 'PUBLIC_REPOSITORY') for p in pm.get('resourceCopies',{})];sdk=[str(Path(p).relative_to(h.TC/'m2/repository')) for p in pm['dependencies'] if p not in [str(h.ANN),str(h.CONSOLE)]]
 c=dict(schema='PGPT_CLOSED_HOST_PROFILE_V1',id='PG28190-'+name.upper(),costWbsLeafIds=['WBS-F03'],costBoundary='ADDITIONAL_QUALIFICATION_NO_ORIGINAL_COST_REASSIGNMENT',productOwnerByMainPath={p:owners[p] for p in main},oracleSpecs=[ref(B/spec)],closureProofs=[ref(po)],qualityExceptions=[],coverageExclusions=[],productionCoreMain=m['productionCoreMain'],mainSources=main,testSources=[dict(path=p,tests=n) for p,n in zip(tests,totals)],expectedTests=sum(totals),resources=resources,sdkJars=sdk,preparedDependencyHashes=pm['dependencies'],physicalClasses=sorted(pm['physicalClassHashes']),targetClasses=sorted(m['targetCounters']),pomInputs=[p for p in pm['inputHashes'] if p=='pom.xml' or p.endswith('/pom.xml')],systemProperties=props,slots={stage:str(B/'evidence'/('PG28190-'+name+'-example-'+stage)) for stage in ['prestyle','prepare','static','preflight','unit','post']},privateDirs={stage:'pg28190-'+name+'-example-'+stage for stage in ['prepare','unit']},newTestDefinitions=0)
 h.validate_syntax(c);h.validate_owners(c,owners);cp=B/'input'/('2036'+name[0]+'_closed_host_example.json');require(not cp.exists(),'immutable example config');wr(cp,c);configs.append(c);cases.append(dict(case='POSITIVE_'+name,config=ref(cp),originalPrepare=ref(pp),originalPost=ref(po),wholeTests=sum(totals),physicalClasses=len(c['physicalClasses']),preparedSdkHashesIdentical=True,selectedClassesMetadataIdentical=sorted({x['classname'] for x in pm['expectedCases']})==pm['selectedClasses'],productTestsExecuted=0))
base=configs[0];negatives=[]
def rejected(name,mutate,owner_check=False):
 c=copy.deepcopy(base);mutate(c)
 try:
  h.validate_syntax(c)
  if owner_check:h.validate_owners(c,owners)
 except ValueError as e:negatives.append(dict(case=name,rejected=True,reason=str(e),metadataOnly=True));return
 raise AssertionError('unsafe metadata accepted: '+name)
rejected('MISSING_EXPLICIT_COST_OWNER',lambda c:c.pop('costWbsLeafIds'))
rejected('CLONED_OTHER_BUSINESS_COST_LABEL',lambda c:c.update(costWbsLeafIds=['WBS-P016-21']))
rejected('MISSING_PRODUCT_OWNERS',lambda c:c.update(productOwnerByMainPath={}))
rejected('MISMATCHED_ARTIFACT_OWNER',lambda c:c['productOwnerByMainPath'].update({c['mainSources'][0]:'WBS-P016-21'}),True)
rejected('PARENT_ESCAPE',lambda c:c['mainSources'].__setitem__(0,'../outside/Example.java'))
rejected('DUPLICATE_SOURCE',lambda c:c['mainSources'].append(c['mainSources'][0]))
rejected('QUALITY_EXCEPTION',lambda c:c.update(qualityExceptions=['ignore']))
rejected('COVERAGE_EXCLUSION',lambda c:c.update(coverageExclusions=['*']))
rejected('WRONG_WHOLE_COUNT',lambda c:c.update(expectedTests=999))
rejected('NEGATIVE_TEST_COUNT',lambda c:c['testSources'][0].update(tests=-1))
rejected('APPLICATION_JAR',lambda c:c.update(sdkJars=['local/schubert-application.jar']))
rejected('UNOWNED_RUNTIME_PROPERTY',lambda c:c.update(systemProperties={'arbitrary.flag':'true'}))
rejected('ROOT_OWNED_OUTPUT',lambda c:c['slots'].update(unit='/outside/run'))
rejected('REUSED_EVIDENCE_SLOT',lambda c:c['slots'].update(unit=c['slots']['prepare']))
rejected('MISSING_CLOSURE_ORACLE',lambda c:c.update(closureProofs=[]))
rejected('MISSING_SDK_PIN',lambda c:c.update(preparedDependencyHashes={}))
rejected('OLD_GROUP_ID_SYNTAX',lambda c:c.update(id='PG28190_BAD_CLONE'))
rejected('DUPLICATE_PHYSICAL_CLASS',lambda c:c['physicalClasses'].append(c['physicalClasses'][0]))
rejected('UNKNOWN_TARGET',lambda c:c.update(targetClasses=['dev/codex/schubert/nk/unknown/Example']))
rejected('PRIVATE_RESOURCE',lambda c:c.update(resources=[dict(path='private/fixture.json',placement='TEST_CLASSPATH')]))
for n in ['pgpt_closed_host_profile','pgpt_closed_host_stages','pgpt_closed_host_post']:
 p=R/'tools/quality'/(n+'.py');compile(p.read_text(),str(p),'exec')
v=dict(actualExit=0,positiveProfiles=cases,negativeChecks=negatives,metadataChecksPassed=len(cases)+len(negatives),toolSources=h.tool_hashes(),rootCompilerPolicy=h.compiler_element()[0] is not None,javaOrMavenProcessesStarted=0,productTestsExecuted=0,oldProductRunsReplayed=0,classOrExecFilesRead=0,newAcceptance=0,formalUpdated=False,effortRate=None,toolRuntimeQualification='PENDING_FIRST_NECESSARY_NEW_PROFILE_NO_PRODUCT_SUCCESS_REPLAY',scope='PURE_SYNTAX_OWNER_METADATA_AND_RECORDED_MANIFEST_FIELDS_ONLY',verifier=ref(Path(__file__).resolve()));wr(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,positive4=len(cases),negative=len(negatives),toolChecks=len(cases)+len(negatives),productTestsExecuted=0,manifest=ref(O/'manifest.json'))))
