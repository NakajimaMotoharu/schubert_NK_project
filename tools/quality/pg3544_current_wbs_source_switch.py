"""Journalled source switch after17/51 criterion proof, never new acceptance."""
import argparse
import collections
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo
import wbs_progress_audit as audit
from pg3282_wbs_current_source_apply import rewrite_root, replace_public, metadata_descriptions, group_coverage
import pg3542_current_criteria_revalidation as review
from pg1446_current_cold_stage import W

ROOT,PMO,SOURCE=review.ROOT,review.PMO,review.SOURCE
OUT=W/'pg3544-current-wbs-source-switch-v1'
PROOF=review.PUBLIC/'manifest.json'
NAMES=('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json','485_WBS網羅性・受入対応.json','486_WBS現行実績.json')
MUTATED=(NAMES[0],NAMES[2],NAMES[3])
RUNTIME={'WBS-N05','WBS-N06','WBS-N07','WBS-N08','WBS-N10','WBS-N12'}


def candidates(texts,proof):
    values={n:json.loads(t,object_pairs_hook=audit.unique_object)for n,t in texts.items()}
    master,budget,inventory,snapshot=(values[n]for n in NAMES)
    review.require(set(proof['rows'])==review.EXPECTED and proof['criteriaRevalidated']==51 and proof['newLeafCredit']==0,'complete explicit17/51 non-new-acceptance proof required')
    review.require(all(review.sha(texts[n].encode())==proof['beforeFileHashes'][n]for n in NAMES),'all four historical masters unchanged since criterion proof')
    acceptance={};tasks=copy.deepcopy(master['tasks'])
    for row in tasks:
        if row['id']not in proof['rows']:continue
        r=proof['rows'][row['id']];old=copy.deepcopy(row['acceptance'])
        review.require(old['status']=='ACCEPTED'and old['source']==review.PREVIOUS,'only historical17 may be rebound')
        row.setdefault('acceptanceHistory',[]).append(old)
        row['acceptance']={**old,'source':SOURCE,'evidence':[{'path':str(PROOF.relative_to(ROOT)),
            'sha256':review.sha(PROOF.read_bytes()),'source':SOURCE,'run':'PG3542-current-criteria-revalidation-v1','verifiedChecks':r['verifiedChecks']}],
            'acceptedBy':'Codex per-criterion current3712/source/scope/oracle/quality/dependency revalidation of existing17; no new leaf credit'}
        acceptance[row['id']]=row['acceptance']
    review.require(set(acceptance)==review.EXPECTED,'all and only existing17 must be revalidated')
    artifacts=copy.deepcopy(inventory['artifacts'])
    for change in proof['onlyPhysicalChange']:
        artifact=next(a for a in artifacts if a['path']==change['path'])
        review.require(artifact['sha256']==change['oldSha256']and artifact['owner']=='WBS-P006-02','one unaccepted Main change only')
        artifact.setdefault('sourceByteHistory',[]).append({'source':review.PREVIOUS,'sha256':artifact['sha256']})
        artifact['sha256']=change['newSha256'];artifact['changeEvidence']='BUG1299/4856b3fca; actual3712/545/1643/current native10points9streams; individual Outbox scope remains NOT_ACCEPTED'
    measurement=review.read(ROOT/review.MEASUREMENT);data=group_coverage(measurement)
    rows=copy.deepcopy(snapshot['rows'])
    for row in rows:
        prior=copy.deepcopy({k:v for k,v in row.items()if k not in {'id','historicalMeasurements','evidence'}})
        prior.update(sourceBinding=snapshot['source'],measurementRun=snapshot['measurementRun'])
        row.setdefault('historicalMeasurements',[]).append(prior)
        row.pop('measurementOverride',None);row.pop('appliesToPendingHostCandidate',None)
        row.pop('currentTechnicalMeasurement',None)
        if row['id']in acceptance:row['acceptance']=copy.deepcopy(acceptance[row['id']])
        if 'measuredFamilies'in row:
            owned=[a for a in artifacts if a['owner']==row['id']and a['kind']=='JAVA'and a['module']in data]
            counts=[];declarations=0
            for artifact in owned:
                count=data[artifact['module']].get(artifact['class'])
                if artifact.get('counterApplicability')=='NO_EXECUTABLE_INTERFACE':
                    review.require(count is not None and all(sum(v)==0 for v in count.values()),'pure declaration still zero executable counters')
                    declarations+=1
                else:counts.append(count)
            status=audit.classify([None if c is None else[c[k][z]for k in ('LINE','METHOD','CLASS','BRANCH')for z in (0,1)]for c in counts])if counts else('NON_EXECUTABLE_CONTRACT_REVIEW'if owned else'NON_JAVA_EVIDENCE_REQUIRED')
            row.update(measurementStatus=status,measurementSource=SOURCE,measuredFamilies=len(counts),
                       missed={k:sum(c[k][0]for c in counts if c is not None)for k in ('LINE','METHOD','CLASS','BRANCH')},nonExecutableFamilies=declarations)
            row['evidence']=[*row['evidence'],review.MEASUREMENT]
        elif row['id']in RUNTIME or row['id']=='WBS-CHR-A01':
            row.update(measurementStatus='VM_STEP_VERIFIED',measurementSource=SOURCE,currentLiveAuthority=False)
            row.pop('sourceRecheckReason',None)
            row['evidence']=[*row['evidence'],'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3534-current-root-owned-native-v1/manifest.json']
            row['currentTechnicalMeasurement']={'productionSource':SOURCE,'run':'PG3534-current-root-owned-native-v1','partialStageNotLeafAcceptance':True,
                'A01OnlyNotFullChr':row['id']=='WBS-CHR-A01','newManufactureCredit':0,'currentLiveAuthority':False}
        elif row['measurementStatus']=='VM_STEP_VERIFIED':
            row.update(measurementStatus='HISTORICAL_VM_SUCCESS_RECHECK',measurementSource=review.PREVIOUS,currentLiveAuthority=False,
                       sourceRecheckReason='Olda9 stage is preserved, not yet fully re-proved on4856; current Root DONE alone does not prove intent/runtime retirement')
        if row['id']in acceptance:row['evidence']=[*row['evidence'],str(PROOF.relative_to(ROOT))]
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    binding={'source':SOURCE,'run':measurement['run'],'coverageRoot':measurement['coverageRoot'],'manifest':review.MEASUREMENT}
    descriptions=metadata_descriptions(SOURCE,measurement['run'],3712,545,1643)
    descriptions['measurementMode']='Current4856 actual3712/545/1643 plus eligible native10points/latest9; olda9/native28 excluded. Technical source rebase and existing17/51 revalidation, new leaf credit0, formal1964/53 unchanged. Older explicitly source-tagged top-level observations remain historical, never current authority.'
    history={'source':inventory['source'],'binding':inventory['measurementBindings'],'preservedGitHead':head,
             'inventorySha256':proof['beforeFileHashes'][NAMES[2]],'snapshotSha256':proof['beforeFileHashes'][NAMES[3]],
             'priorArtifactHashMeaning':inventory.get('artifactHashMeaning'),'priorMeasurementMode':snapshot.get('measurementMode'),
             'newCriterionManifest':str(PROOF.relative_to(ROOT)),'newCriterionManifestSha256':review.sha(PROOF.read_bytes()),'newAcceptedLeafDelta':0}
    mastertext=rewrite_root(texts[NAMES[0]],{'tasks':tasks})
    inventorytext=rewrite_root(texts[NAMES[2]],{'source':SOURCE,'assessmentHead':head,'artifacts':artifacts,
      'artifactHashMeaning':descriptions['artifactHashMeaning'],'measurementBindings':binding,
      'measurementBindingHistory':[*inventory.get('measurementBindingHistory',[]),history]})
    snapshottext=rewrite_root(texts[NAMES[3]],{'source':SOURCE,'measurementRun':measurement['run'],'measurementMode':descriptions['measurementMode'],
      'asOf':datetime.datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(),'inventorySha256':review.sha(inventorytext.encode()),
      'rows':rows,'counts':dict(collections.Counter(r['measurementStatus']for r in rows)),
      'currentSourceRevalidation20261016':{'source':SOURCE,'previousSource':review.PREVIOUS,'acceptedRevalidated':17,'individualCriteriaRevalidated':51,
        'newAcceptedLeafDelta':0,'physicalChanges':1,'measurementNativePoints':10,'latestNativeStreams':9,'oldSourceNativeImported':False,
        'runtimeRowsRevalidated':sorted(RUNTIME),'A01MeasuredNotFullGate':True,'N09IntentAndN14RetirementStillNeedCurrentProof':True,
        'remaining':measurement['remaining'],'effortPercent':None,'formalUpdated':False,'F03Accepted':False,'criteriaManifest':str(PROOF.relative_to(ROOT))}})
    return {NAMES[0]:mastertext,NAMES[1]:texts[NAMES[1]],NAMES[2]:inventorytext,NAMES[3]:snapshottext}


def stage():
    review.require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean committed fixed source proof/tools required')
    proof=review.read(PROOF);texts={n:(PMO/n).read_text()for n in NAMES};new=candidates(texts,proof)
    os.umask(0o077);OUT.mkdir(mode=0o700)
    for name in NAMES:
        with(OUT/('before-'+name)).open('x')as f:f.write(texts[name])
        with(OUT/('candidate-'+name)).open('x')as f:f.write(new[name])
    result=audit.verify(master_path=OUT/('candidate-'+NAMES[0]),budget_path=OUT/('candidate-'+NAMES[1]),
                        inventory_path=OUT/('candidate-'+NAMES[2]),snapshot_path=OUT/('candidate-'+NAMES[3]))
    review.require(result['acceptedTasks']==17,'no new accepted leaf allowed')
    record={'actualExit':0,'productionSource':SOURCE,'oldHashes':proof['beforeFileHashes'],
            'newHashes':{n:review.sha(new[n].encode())for n in NAMES},'audit':result,
            'criterionManifestSha256':review.sha(PROOF.read_bytes()),'applied':False,'newLeafCredit':0}
    with(OUT/'stage.safe.json').open('x')as f:json.dump(record,f,sort_keys=True)
    print(json.dumps({'actualExit':0,'staged':True,'source':SOURCE,'acceptedTasks':result['acceptedTasks'],'counts':result['currentMeasurementCounts'],'newLeafCredit':0,'applied':False}));return 0


def apply():
    review.require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean fixed apply operator required')
    r=review.read(OUT/'stage.safe.json')
    review.require(r['actualExit']==0 and r['applied']is False and not(OUT/'apply-intent.safe.json').exists(),'one staged application only; interrupted intent must recover explicitly')
    review.require(review.sha(PROOF.read_bytes())==r['criterionManifestSha256'],'immutable complete criterion proof required')
    for name in NAMES:
        review.require(review.sha((PMO/name).read_bytes())==r['oldHashes'][name],'concurrent master change detected')
        review.require(review.sha((OUT/('candidate-'+name)).read_bytes())==r['newHashes'][name],'staged candidate byte changed')
    with(OUT/'apply-intent.safe.json').open('x')as f:json.dump({'oldHashes':r['oldHashes'],'newHashes':r['newHashes'],'mutated':MUTATED},f,sort_keys=True);f.flush();os.fsync(f.fileno())
    fd=os.open(OUT,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
    for name in MUTATED:replace_public(PMO/name,(OUT/('candidate-'+name)).read_bytes())
    result=audit.verify();review.require(result['acceptedTasks']==17,'canonical audit and unchanged accepted17 required')
    record={'actualExit':0,'productionSource':SOURCE,'applied':True,'newLeafCredit':0,'acceptedRevalidated':17,'criteriaRevalidated':51,'audit':result,
            'newHashes':{n:review.sha((PMO/n).read_bytes())for n in NAMES}}
    with(OUT/'apply.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'applied':True,'acceptedTasks':result['acceptedTasks'],'newLeafCredit':0}));return 0


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply']);raise SystemExit({'stage':stage,'apply':apply}[p.parse_args().action]())
