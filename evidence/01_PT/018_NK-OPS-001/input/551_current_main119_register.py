"""Current Main path inventory only, explicit reviewed responsibilities; never executes Main."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,json,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001'
C=B/'input/549_current_main119_trace_scope.json';D=B/'input/552_current_main119_owner_decisions.json';O=B/'evidence/PG23850-current-main119-inventory-register-v1'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=load(C);dec=load(D);assert not O.exists();wp=R/cfg['wbsBefore']['path'];assert sha(wp)==cfg['wbsBefore']['sha256'];wb=load(wp)
normal=Path(cfg['normalManifest']['path']);assert sha(normal)==cfg['normalManifest']['sha256'];nm=load(normal);assert nm['actualExit']==0 and nm['source']==cfg['source']
indexp=B/'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';assert sha(indexp)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723';index=load(indexp)
wbs=load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json');tasks={v['id']:v for v in wbs['tasks']}
for ref in dec['authorityReferences']:assert sha(R/ref['path'])==ref['sha256']
known={v['path']:v for v in wb['artifacts']};assert len(known)==len(wb['artifacts'])==942
tracked=subprocess.check_output(['git','ls-files','--',':(glob)src/**/src/main/java/**/*.java'],cwd=R,text=True).splitlines()
assert sorted(tracked)==cfg['productionMainPaths'] and len(tracked)==967
assert set(tracked)-set(known)==set(cfg['missingSourcePins']) and len(set(tracked)&set(known))==848
assert subprocess.run(['git','diff','--quiet',cfg['source'],'--',':(glob)src/**/src/main/java/**/*.java'],cwd=R).returncode==0
observ=B/'evidence/PG23848-main119-role-observations-v1/source-role-observations.json';observed={v['path']:v for v in load(observ)}
assert len(dec['decisions'])==119 and {v['path'] for v in dec['decisions']}==set(cfg['missingSourcePins'])
added=[];evidence=[]
for d in dec['decisions']:
 n=d['path'];assert n not in known and not any(t in n for t in cfg['protectedNameTokens']);p=R/n
 assert p.stat().st_size<=cfg['maxSourceBytes'] and sha(p)==d['sourceSha256']==cfg['missingSourcePins'][n]==nm['begin']['inputHashes'][n]
 assert observed[n]['classDoc']==d['reviewedDeclaredResponsibility'] and d['owner']==d['costOwner'] and d['owner'] in tasks
 owner=tasks[d['owner']];physical={k:v for k,v in index.items() if v['path']==n};assert physical
 classname=observed[n]['package'].replace('.','/')+'/'+Path(n).stem;assert classname in physical
 code=any(v['hasCode'] for v in physical.values());isPackage=Path(n).name=='package-info.java';assert not isPackage or not code
 row=dict(path=n,kind='JAVA',module=n.split('/')[1].removeprefix('schubert-nk-'),**{'class':classname},owner=d['owner'],costOwner=d['costOwner'],basis='PG23850 explicit per-source responsibility decision552 and pinned full public Main identity; no coverage/requirement acceptance.',sha256=d['sourceSha256'],acceptance='UNASSESSED',counterApplicability='EXECUTABLE_OR_MEASUREMENT_REQUIRED' if code else 'NO_EXECUTABLE_CODE_METADATA_PHYSICAL_RETAINED')
 added.append(row)
 evidence.append(dict(path=n,sourceSha256=d['sourceSha256'],className=classname,module=row['module'],canonicalOwner=d['owner'],canonicalCostOwner=d['costOwner'],program=owner['program'],ownerTitle=owner['title'],reason=d['reason'],reviewedDeclaredResponsibility=d['reviewedDeclaredResponsibility'],declaredProgramReferences=d['declaredProgramReferences'],declaredDocumentReferences=d['declaredDocumentReferences'],ownerRequirementDomain=owner['requirementIds'],requirementMappingStatus='OWNER_DOMAIN_AND_DECLARED_REFERENCES_ONLY_NOT_COMPLETE_REQUIREMENT_JOIN',wholeSourcePhysicalClasses=sorted(physical),physicalClassHashes={k:v['sha256'] for k,v in physical.items()},physicalClassHasCode={k:v['hasCode'] for k,v in physical.items()},executablePhysicalClasses=sum(v['hasCode'] for v in physical.values()),isPackageAnnotationMetadata=isPackage,noExecutableCodeInSource=not code,noCodeCounterRatio=None,coverageQualified=False,wholeRequirementTraceAccepted=False,wholeG13Accepted=False))
assert len(added)==119 and sum(v['noExecutableCodeInSource'] for v in evidence)==6
oldRows=wb['artifacts'][:];wb['artifacts']+=added;assert len(wb['artifacts'])==1061
assert len({v['path'] for v in wb['artifacts']})==1061 and set(tracked)<={v['path'] for v in wb['artifacts']}
key='currentMainPathInventoryCompletion20261108';assert key not in wb
O.mkdir()
for name,value in [('added-artifacts.json',added),('source-owner-proof.json',evidence),('current-main-paths.json',sorted(tracked))]:
 (O/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
files={n:sha(O/n) for n in ('added-artifacts.json','source-owner-proof.json','current-main-paths.json')}
wb[key]=dict(source=cfg['source'],mainPathCount=967,registeredBefore=848,registeredAfter=967,missingAfter=0,duplicateCurrentPaths=0,newArtifactRows=119,totalArtifactRowsAfter=1061,ownerCounts=dict(Counter(v['owner'] for v in added)),noExecutableCodeAddedSources=6,packageAnnotationMetadataAddedSources=3,legacyCountsSnapshotNotReinterpreted=True,sourceTrace=dict(path=str((O/'source-owner-proof.json').relative_to(R)),sha256=files['source-owner-proof.json']),manifest=str((O/'manifest.json').relative_to(R)),scope='CURRENT_MAIN_PATH_INVENTORY_ONLY_NOT_COMPLETE_METHOD_REQUIREMENT_TEST_OR_WHOLE_G13_451',newProductTests=0,newAcceptance=0,wholeG13Accepted=False,whole451Accepted=False,effortRate=None)
wp.write_text(json.dumps(wb,ensure_ascii=False,indent=2)+'\n')
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],observerHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),config=dict(path=str(C.relative_to(R)),sha256=sha(C)),decisions=dict(path=str(D.relative_to(R)),sha256=sha(D)),wbsBefore=cfg['wbsBefore'],wbsAfter=dict(path=str(wp.relative_to(R)),sha256=sha(wp)),overlayKey=key,mainPaths=967,registeredBefore=848,registeredAfter=967,missingBefore=119,missingAfter=0,addedRows=119,artifactRowsBefore=942,artifactRowsAfter=1061,ownerCounts=dict(Counter(v['owner'] for v in added)),noExecutableCodeSources=6,packageAnnotationMetadataSources=3,sourceTreeIdenticalToNormal7aed=True,sourceBodiesReadAsDataOnly=True,wholeBehaviorReviewClaimed=False,oldArtifactRowsUnchanged=True,productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,heldFourInitializations=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,files=files,bugs=['BUG-2504'],ykts=['YKT-2242'],tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,main=967,registered=967,added=119,missing=0,noCodeSources=6,owners=out['ownerCounts'],manifestSha256=sha(O/'manifest.json'))))
