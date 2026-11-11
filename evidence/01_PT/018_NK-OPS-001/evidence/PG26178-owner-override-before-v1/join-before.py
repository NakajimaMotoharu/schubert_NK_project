"""G13.07/1 current public responsibility join; no runtime qualification or Test IO."""
import collections,datetime,hashlib,json,subprocess
from pathlib import Path
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';D=R/'documents/400_PGPT/470_PMO';E=B/'evidence';O=E/'PG26176-six-domain-initial-owner-join-v1';assert not O.exists()
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=E/'PG22122-current7aed-lineage-style-v1/artifacts.json';assert sha(p)=='fb24a1a209849d42894925002baae668bc55a4bd858b1b7c1d38ab838319bb0b';artifacts=load(p);w=load(D/'481_PGPT詳細WBS.json');inv=load(D/'485_WBS網羅性・受入対応.json');tasks={x['id']:x for x in w['tasks']};byPath={x['path']:x for x in artifacts};assert len(byPath)==len(artifacts)==1068
counts=collections.Counter(x['owner'] for x in artifacts);assert dict(counts)==w['currentSourceArtifactOwnershipProjection20261108']['ownerArtifactCounts'];tracked=set(subprocess.check_output(['git','ls-files'],text=True).splitlines());groups=collections.defaultdict(list)
for x in artifacts:
 assert x['owner'] in tasks and x['costOwner'] in tasks and x['path'] in tracked
 domain='deployment' if x['path'].startswith('src/deployment/') else 'characterization' if x['path'].startswith('program/') else x['path'].split('/')[1].removeprefix('schubert-nk-')
 groups[domain].append(x['path'])
physical=load(E/'PG23972-current-main-method-delta42-v1/class-method-inventory.json');physicalOwners=collections.Counter();held=[]
for x in physical:
 assert x['sourcePath'] in byPath and x['owner']==byPath[x['sourcePath']]['owner'] and x['costOwner']==byPath[x['sourcePath']]['costOwner'];physicalOwners[x['owner']]+=1
 if x['structure'] is None:held.append(x['physicalKey'])
references=[]
for x in inv['sharedOwnership']:
 path='src/schubert-nk-'+x['module']+'/src/main/java/'+x['class']+'.java';a=byPath.get(path)
 references.append(dict(sourcePath=path,declaredOwner=x['owner'],currentSourceOwner=a['owner'] if a else None,consumers=x['consumers'],qualification='CURRENT_REFERENCE_ONLY_NOT_SECOND_IMPLEMENTATION' if a and a['owner']==x['owner'] else 'HISTORICAL_OR_UNRESOLVED_REFERENCE_NOT_CURRENT_OWNER',commonImplementationChargedOnce=x['commonImplementationChargedOnce'],consumerRule=x['consumerRule']))
rows=[]
for owner,n in sorted(counts.items()):
 t=tasks[owner];candidates=t['evidencePlan']['candidateTestFiles'];deps=t['dependencies'];assert all(d in tasks for d in deps)
 rows.append(dict(owner=owner,currentArtifactCount=n,currentPhysicalCount=physicalOwners[owner],sourcePaths=[x['path'] for x in artifacts if x['owner']==owner],requirements=t['requirementIds'],relatedRd=t['rd'],relatedUi=t['ui'],relatedSs=t['ss'],candidateTestFileNames=candidates,candidatePathsMissingFromTrackedInventory=[p for p in candidates if p not in tracked],endingDependencies=deps,originalStatus=t['acceptance']['status'],individualMethodOracleQualification='NOT_VERIFIED_BY_RESPONSIBILITY_JOIN',currentSourceAcceptance=False))
O.mkdir();data={'domain-artifact-names.json':dict(groups),'current-owner-and-ending-gaps.json':rows,'shared-reference-only-classification.json':references}
for n,x in data.items():(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',currentArtifacts=len(artifacts),currentPhysicalClasses=len(physical),domains={k:len(v) for k,v in groups.items()},sourceOwners=len(counts),unownedArtifacts=0,duplicateArtifactPaths=0,ownerProjectionCountConflicts=0,physicalSourceOwnerConflicts=0,sharedReferenceRows=len(references),unresolvedSharedReferences=sum(x['qualification']!='CURRENT_REFERENCE_ONLY_NOT_SECOND_IMPLEMENTATION' for x in references),candidateFileNameGaps=sum(len(x['candidatePathsMissingFromTrackedInventory']) for x in rows),heldUnknownPhysicalStructures=held,sourceOwnerCountsAreNotBehaviorQualification=True,individualCriteriaOraclesVerified=False,finalCandidateJoinAccepted=False,productTestsExecuted=0,newAcceptance=0,newCoverageMeasurements=0,actualClassOrTestFileReads=0,actualVmDbRootKeyActions=0,files={n:sha(O/n) for n in data},toolSha256=sha(Path(__file__)),remaining=['Each original owner individual TestID/independent expected/null/boundary/error/parallel/retry and current-source/run/451 ending required.','Initial ownership join does not close G13.07/2 final candidate many-to-many requirements/layout64/CHR24 mapping.','HOLD structures remain unobserved and do not grant actual read/compile/init.'])
(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in m.items() if k in ['actualExit','currentArtifacts','currentPhysicalClasses','domains','sourceOwners','sharedReferenceRows','unresolvedSharedReferences','candidateFileNameGaps','productTestsExecuted','newAcceptance']}))
