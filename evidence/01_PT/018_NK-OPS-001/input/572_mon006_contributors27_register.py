"""Explicit supporting-component references, distinct from annotations or requirement acceptance."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,json,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';C=B/'input/570_mon006_contributors27_scope.json';O=B/'evidence/PG23904-mon006-contributor27-trace-v1'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=load(C);assert not O.exists();wp=R/cfg['wbsBefore']['path'];assert sha(wp)==cfg['wbsBefore']['sha256'];wb=load(wp)
p=R/cfg['priorDeclaredRows']['path'];assert sha(p)==cfg['priorDeclaredRows']['sha256'];prior={v['path']:v for v in load(p)}
for ref in cfg['authority']:
 p=R/ref['path'];assert sha(p)==ref['sha256'] and p.read_bytes()==subprocess.check_output(['git','show','origin/main:'+ref['path']],cwd=R)
rd=next(v for v in wb['requirements'] if v['id']=='MON-006');assert all(word in rd['requirement'] for word in ['JVM','heap','GC','DB connection pool','ディスク残量','HTTP応答時間'])
artifacts={v['path']:v for v in wb['artifacts']};rows=[]
for d in cfg['manualDecisions']:
 n=d['path'];old=prior[n];assert old['status']=='DOCUMENT_OR_OWNER_CONTEXT_ONLY_PRECISE_RD_MAPPING_PENDING' and old['parsed']['ids']==[]
 assert old['sourceSha256']==d['sourceSha256']==artifacts[n]['sha256'] and old['classDeclaration']==d['declaredResponsibility']
 assert d['requirement']=='MON-006' and d['implementationAccepted'] is False and d['actualMeasurementProven'] is False and d['ptAccepted'] is False
 row=dict(d);row.update(canonicalRequirement=rd,owner=artifacts[n]['owner'],costOwner=artifacts[n]['costOwner'],authorityReferences=cfg['authority'],status='DERIVED_SUPPORTING_COMPONENT_REFERENCE_ONLY',explicitCodeRequirementAnnotation=False,originalDeclaredReferenceIds=[],originalPendingStatus=old['status'],wholeG13Accepted=False,whole451Accepted=False);rows.append(row)
assert len(rows)==len({v['path'] for v in rows})==27
assert Counter(v['contributionKind'] for v in rows)=={'JVM_GC_SYSTEM':9,'DB_POOL':9,'HEAP':4,'DISK':2,'HTTP_LATENCY':3}
pending=[n for n,v in prior.items() if v['status']=='DOCUMENT_OR_OWNER_CONTEXT_ONLY_PRECISE_RD_MAPPING_PENDING' and n not in {r['path'] for r in rows}];assert len(pending)==73
O.mkdir();(O/'contributor-links.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');(O/'remaining-precise-mapping.json').write_text(json.dumps(sorted(pending),ensure_ascii=False,indent=2)+'\n');files={n:sha(O/n) for n in ('contributor-links.json','remaining-precise-mapping.json')}
key='currentMonitoringMon006Contributor27Trace20261108';assert key not in wb
wb[key]=dict(source=cfg['source'],sourcePrograms=27,requirement='MON-006',referenceKind='DERIVED_SUPPORTING_COMPONENT_NOT_EXPLICIT_CODE_ANNOTATION',categoryCounts=dict(Counter(v['contributionKind'] for v in rows)),reference=dict(path=str((O/'contributor-links.json').relative_to(R)),sha256=files['contributor-links.json']),remainingPreciseMapping=73,remainingReference=dict(path=str((O/'remaining-precise-mapping.json').relative_to(R)),sha256=files['remaining-precise-mapping.json']),original12Declared84LinksUnchanged=True,actualMeasurementProven=False,implementedRequirementsInferred=False,newProductTests=0,newAcceptance=0,wholeG13Accepted=False,whole451Accepted=False,effortRate=None)
wp.write_text(json.dumps(wb,ensure_ascii=False,indent=2)+'\n')
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],observerHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),config=dict(path=str(C.relative_to(R)),sha256=sha(C)),wbsBefore=cfg['wbsBefore'],wbsAfter=dict(path=str(wp.relative_to(R)),sha256=sha(wp)),overlayKey=key,supportingSourceReferences=27,requirement='MON-006',categoryCounts=dict(Counter(v['contributionKind'] for v in rows)),preciseMappingPendingBefore=100,preciseMappingPendingAfter=73,original12Declared84LinksUnchanged=True,actualMeasurementProven=False,sourceBodiesReread=False,sourceMutation=False,productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,heldFourInitializations=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,files=files,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,supportingSources=27,pending=73,categories=out['categoryCounts'],manifestSha256=sha(O/'manifest.json'))))
