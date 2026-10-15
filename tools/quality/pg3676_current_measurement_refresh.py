"""Same-source technical measurement refresh only; all190 acceptance/cost/scope unchanged."""
import argparse
import collections
import copy
import datetime
import hashlib
import json
import os
import subprocess
from zoneinfo import ZoneInfo
import wbs_progress_audit as audit
from pg3282_wbs_current_source_apply import rewrite_root,replace_public,group_coverage,metadata_descriptions
from pg1446_current_cold_stage import W
from pg3564_current_browser_resume_sources import SOURCE

ROOT=audit.ROOT
PMO=ROOT/'documents/400_PGPT/470_PMO'
OUT=W/'pg3676-current-measurement-refresh-v1'
NAMES=('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json','485_WBS網羅性・受入対応.json','486_WBS現行実績.json')
MEASUREMENT='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3632-current-native-measurement-v1/manifest.json'
PATH_PROOF='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3670-current-browser-resume-native-retired-v1/manifest.json'
INTENT_PROOF='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3674-current-intent-runtime-receipt-v1/manifest.json'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def require(v):
    if not v:raise ValueError('same-source current measurement refresh refused')


def candidates(texts):
    master,budget,inventory,snapshot=(json.loads(texts[n],object_pairs_hook=audit.unique_object)for n in NAMES)
    require(inventory['source']==snapshot['source']==SOURCE)
    require(inventory['measurementBindings']['run']==snapshot['measurementRun']=='PG3532-current-native-measurement-v3')
    old_measurement=json.loads((ROOT/inventory['measurementBindings']['manifest']).read_bytes())
    measurement=json.loads((ROOT/MEASUREMENT).read_bytes());path=json.loads((ROOT/PATH_PROOF).read_bytes());intent=json.loads((ROOT/INTENT_PROOF).read_bytes())
    require(measurement['actualExit']==path['actualExit']==intent['actualExit']==0 and measurement['productionSource']==path['productionSource']==intent['productionSource']==SOURCE)
    require(measurement['nativeStreams']==18 and measurement['validatedNativePoints']==20 and measurement['tests']==3712 and measurement['mainClasses']==1643 and measurement['oldSourceNativeImported']is False)
    require(intent['result']['noStartupStartIntents']and intent['result']['noMaintenanceActiveOriginal']and intent['result']['exactUsedRuntimeAbsent']and intent['result']['currentOriginalNormalWarning10'])
    require(path['individualAccepted']==17 and path['formalAccepted']is False)
    delta={k:old_measurement['remaining'][k]-measurement['remaining'][k]for k in ('LINE','METHOD','CLASS','BRANCH')}
    require(delta=={'LINE':147,'METHOD':24,'CLASS':4,'BRANCH':10})
    data=group_coverage(measurement);rows=copy.deepcopy(snapshot['rows']);artifacts=inventory['artifacts']
    for row in rows:
        if 'measuredFamilies'not in row and row['id']not in {'WBS-N09','WBS-N14'}:continue
        prior=copy.deepcopy({k:v for k,v in row.items()if k not in {'id','historicalMeasurements'}})
        prior.update(sourceBinding=SOURCE,measurementRun=snapshot['measurementRun'])
        row.setdefault('historicalMeasurements',[]).append(prior)
        if 'measuredFamilies'in row:
            targets=[a for a in artifacts if a['owner']==row['id']and a['kind']=='JAVA'and a['module']in data]
            counts=[];declarations=0
            for artifact in targets:
                counter=data[artifact['module']].get(artifact['class'])
                if artifact.get('counterApplicability')=='NO_EXECUTABLE_INTERFACE':
                    require(counter is not None and all(sum(v)==0 for v in counter.values()));declarations+=1
                else:counts.append(counter)
            status=audit.classify([None if c is None else[c[k][z]for k in ('LINE','METHOD','CLASS','BRANCH')for z in (0,1)]for c in counts])if counts else('NON_EXECUTABLE_CONTRACT_REVIEW'if targets else'NON_JAVA_EVIDENCE_REQUIRED')
            row.update(measurementStatus=status,measurementSource=SOURCE,measuredFamilies=len(counts),nonExecutableFamilies=declarations,missed={k:sum(c[k][0]for c in counts if c is not None)for k in ('LINE','METHOD','CLASS','BRANCH')})
            row.pop('measurementOverride',None);row['evidence']=[*row['evidence'],MEASUREMENT]
        else:
            row.update(measurementStatus='VM_STEP_VERIFIED',measurementSource=SOURCE,currentLiveAuthority=False)
            row.pop('sourceRecheckReason',None)
            row['evidence']=[*row['evidence'],PATH_PROOF,INTENT_PROOF]
            row['currentTechnicalMeasurement']={'productionSource':SOURCE,'run':'PG3670-current-browser-resume-native-retired-v1','partialStageNotLeafAcceptance':True,'genuineNormalWarning10WithinOriginal1800s':True,'normalOwnedStopAndIndependentAll24Resources0':True,'noStartIntentsAndNormalOriginalVerified':True,'usedRuntimeExactRetirementAndFull11Native34Preserved':True,'runtimeDirectoryAuthorityIssued':False,'currentLiveAuthority':False,'exitDependenciesAndWholeQualityAccepted':False}
    require({r['id']:r['acceptance']for r in rows}=={r['id']:r['acceptance']for r in snapshot['rows']})
    require(sum(r['acceptance']['status']=='ACCEPTED'for r in rows)==17)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    binding={'source':SOURCE,'run':measurement['run'],'coverageRoot':measurement['coverageRoot'],'manifest':MEASUREMENT}
    description=metadata_descriptions(SOURCE,measurement['run'],3712,545,1643)
    history={'source':SOURCE,'binding':inventory['measurementBindings'],'preservedGitHead':head,'inventorySha256':sha(texts[NAMES[2]].encode()),'snapshotSha256':sha(texts[NAMES[3]].encode()),'newAcceptedLeafDelta':0,'reason':'Same Main/Test/source; two eligible current cohorts20points18streams and explicit N09/N14 terminated runtime proof. No acceptance or authority rebind.'}
    inventorytext=rewrite_root(texts[NAMES[2]],{'assessmentHead':head,'artifactHashMeaning':description['artifactHashMeaning'],'measurementBindings':binding,'measurementBindingHistory':[*inventory.get('measurementBindingHistory',[]),history]})
    snapshottext=rewrite_root(texts[NAMES[3]],{'asOf':datetime.datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(),'measurementRun':measurement['run'],'measurementMode':'Current4856 same3712/545/1643 + two eligible current cohorts20points/latest18; no old-source import. Limited terminated runtime N09/N14 proof, not individual acceptance/global100/F03/formal.','inventorySha256':sha(inventorytext.encode()),'rows':rows,'counts':dict(collections.Counter(r['measurementStatus']for r in rows)),
        'currentBrowserResumeAndRuntimeClosure20261016':{'productionSource':SOURCE,'publicPathManifest':PATH_PROOF,'publicPathSha256':sha((ROOT/PATH_PROOF).read_bytes()),'currentIntentManifest':INTENT_PROOF,'currentIntentSha256':sha((ROOT/INTENT_PROOF).read_bytes()),'currentNativeManifest':MEASUREMENT,'currentNativeSha256':sha((ROOT/MEASUREMENT).read_bytes()),'nativePoints':20,'latestStreams':18,'remaining':measurement['remaining'],'deltaFromPriorCurrent':delta,'runtimeRowsRevalidated':['WBS-N09','WBS-N14'],'supersedesCurrentStateOf':['currentSourceRevalidation20261016.N09IntentAndN14RetirementStillNeedCurrentProof'],'formalUpdated':False,'acceptedLeafDelta':0,'effortPercent':None,'F03Accepted':False,'currentLiveAuthority':False}})
    return {NAMES[0]:texts[NAMES[0]],NAMES[1]:texts[NAMES[1]],NAMES[2]:inventorytext,NAMES[3]:snapshottext}


def stage():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT));audit.verify()
    texts={n:(PMO/n).read_text()for n in NAMES};new=candidates(texts)
    os.umask(0o077);OUT.mkdir(mode=0o700)
    for n in NAMES:
        (OUT/('before-'+n)).write_text(texts[n]);(OUT/('candidate-'+n)).write_text(new[n])
    result=audit.verify(master_path=OUT/('candidate-'+NAMES[0]),budget_path=OUT/('candidate-'+NAMES[1]),inventory_path=OUT/('candidate-'+NAMES[2]),snapshot_path=OUT/('candidate-'+NAMES[3]));require(result['acceptedTasks']==17)
    value={'actualExit':0,'oldHashes':{n:sha(texts[n].encode())for n in NAMES},'newHashes':{n:sha(new[n].encode())for n in NAMES},'audit':result,'applied':False,'newLeafCredit':0}
    with(OUT/'stage.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps({'actualExit':0,'staged':True,'audit':result}));return 0


def apply():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT));v=json.loads((OUT/'stage.safe.json').read_bytes());require(v['actualExit']==0 and not(OUT/'apply-intent.safe.json').exists())
    for n in NAMES:require(sha((PMO/n).read_bytes())==v['oldHashes'][n]and sha((OUT/('candidate-'+n)).read_bytes())==v['newHashes'][n])
    with(OUT/'apply-intent.safe.json').open('x')as f:json.dump({'oldHashes':v['oldHashes'],'newHashes':v['newHashes'],'mutated':list(NAMES[2:])},f,sort_keys=True);f.flush();os.fsync(f.fileno())
    directory=os.open(OUT,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(directory)
    finally:os.close(directory)
    for n in NAMES[2:]:replace_public(PMO/n,(OUT/('candidate-'+n)).read_bytes())
    result=audit.verify();require(result['acceptedTasks']==17)
    with(OUT/'apply.safe.json').open('x')as f:json.dump({'actualExit':0,'applied':True,'audit':result,'newLeafCredit':0},f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'applied':True,'audit':result}));return 0


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply']);raise SystemExit({'stage':stage,'apply':apply}[p.parse_args().action]())
