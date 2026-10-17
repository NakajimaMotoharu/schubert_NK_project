"""Journalled mechanical dual-inventory update; no Production/acceptance/cost mutation."""
import argparse
import copy
import json
import os
import subprocess
from pathlib import Path
import wbs_progress_audit as audit
import wbs_candidate_trace as trace
from pg3282_wbs_current_source_apply import rewrite_root,replace_public

ROOT=audit.ROOT
PMO=ROOT/'documents/400_PGPT/470_PMO'
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=W/'pg4946-current-physical-trace-v1'
SOURCE='04bbdb73b532537e3546191d72dee913b17629a0'
DESIGN='44d23bb6146237e82af8c137cbfb69903cfb55fa'
PUBLIC='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4942-current-bootstrap-native-v1/manifest.json'
PROOF='80084b366f203a44ab8c68c8e1cd54cb6fb77a852eb695080787165fb2cde07b'
NAMES=('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json','485_WBS網羅性・受入対応.json','486_WBS現行実績.json')
require=trace.require
sha=trace.sha


def candidates(texts):
    require(sha((ROOT/PUBLIC).read_bytes())==PROOF,'actual current qualified native/public proof')
    inventory,snapshot=(json.loads(texts[n],object_pairs_hook=audit.unique_object)for n in NAMES[2:])
    require('currentPhysicalCandidate'not in inventory,'initial dual inventory only; do not overwrite newer candidate')
    old=inventory['artifacts'];paths=[trace.MOVES.get(a['path'],a['path'])for a in old]
    old_blobs=trace.git_artifacts(inventory['source'],[a['path']for a in old])
    require(all(sha(old_blobs[a['path']])==a['sha256']for a in old),'all941 old descriptors exact original Git bytes')
    current=trace.git_artifacts(SOURCE,paths);artifacts=[]
    for original,path in zip(old,paths,strict=True):
        artifact={k:original[k]for k in ('kind','owner','costOwner')}
        artifact.update(path=path,historicalPath=original['path'],sha256=sha(current[path]),acceptance='UNASSESSED')
        if artifact['kind']=='JAVA':
            artifact.update(module=path.split('/')[1].removeprefix('schubert-nk-'),class_=path.split('/src/main/java/',1)[1][:-5])
            artifact['class']=artifact.pop('class_')
        artifacts.append(artifact)
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
    candidate={'version':1,'source':SOURCE,'historicalSource':inventory['source'],
      'historicalDescriptorSha256':trace.descriptor_digest(old),'relocations':trace.MOVES,
      'design':{'source':DESIGN,'path':design,'sha256':sha(trace.git_artifacts(DESIGN,[design])[design])},
      'measurement':{'path':PUBLIC,'sha256':PROOF},'artifacts':artifacts,
      'acceptedLeafDelta':0,'scopeChanged':False,'effortPercent':None}
    proposal=copy.deepcopy(inventory);proposal['currentPhysicalCandidate']=candidate
    measured=trace.verify_candidate(proposal)
    current_text=rewrite_root(texts[NAMES[2]],{
      'currentPhysicalCandidate':candidate,
      'artifactHashMeaning':'artifacts bind immutable historical Git source '+inventory['source']+' and its canonical measurement/17 acceptances. currentPhysicalCandidate independently binds current signed '+SOURCE+' Git/worktree bytes, two SSC295 relocations and all-six native XML. Neither hashes nor counters grant acceptance/runtime authority.',
      'currentCandidateAssessmentHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()})
    snapshot_text=rewrite_root(texts[NAMES[3]],{
      'inventorySha256':sha(current_text.encode()),'currentPhysicalCandidateMeasurement':measured,
      'candidateInventoryMeaning':'Historical7fff descriptors/measurement/individual17 remain unchanged; currentPhysicalCandidate contains all941 current04bb families and independently validated native technical counters. Current candidate criteria UNASSESSED; original costs/formal/effortnull unchanged.'})
    return {**texts,NAMES[2]:current_text,NAMES[3]:snapshot_text}


def stage():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean fixed dual inventory stage')
    require(not subprocess.check_output(['git','diff',SOURCE,'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT),'signed current Main/Test/settings unchanged')
    texts={n:(PMO/n).read_text()for n in NAMES};proposed=candidates(texts)
    os.umask(0o077);OUT.mkdir(mode=0o700)
    for n in NAMES:
        (OUT/('before-'+n)).write_text(texts[n]);(OUT/('candidate-'+n)).write_text(proposed[n])
    result=audit.verify(master_path=OUT/('candidate-'+NAMES[0]),budget_path=OUT/('candidate-'+NAMES[1]),inventory_path=OUT/('candidate-'+NAMES[2]),snapshot_path=OUT/('candidate-'+NAMES[3]))
    require(result['acceptedTasks']==17,'historical17 unchanged')
    record={'actualExit':0,'before':{n:sha(texts[n].encode())for n in NAMES},'after':{n:sha(proposed[n].encode())for n in NAMES},'proofSha256':PROOF,'audit':result,'newAcceptedLeafDelta':0}
    (OUT/'stage.safe.json').write_text(json.dumps(record,sort_keys=True));print(json.dumps({'actualExit':0,'staged':True,'historicalAcceptedTasks':17,'currentCandidate':result['currentPhysicalCandidate']}));return 0


def apply():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean fixed dual inventory apply')
    record=json.loads((OUT/'stage.safe.json').read_bytes())
    require(record['actualExit']==0 and not(OUT/'apply-intent.safe.json').exists()and sha((ROOT/PUBLIC).read_bytes())==record['proofSha256']==PROOF,'one current qualified staged apply')
    for n in NAMES:
        require(sha((PMO/n).read_bytes())==record['before'][n]and sha((OUT/('candidate-'+n)).read_bytes())==record['after'][n],'no concurrent metadata change')
    with(OUT/'apply-intent.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    for n in NAMES[2:]:replace_public(PMO/n,(OUT/('candidate-'+n)).read_bytes())
    result=audit.verify();require(result['acceptedTasks']==17,'historical acceptance17 retained')
    require(all(sha((PMO/n).read_bytes())==record['before'][n]for n in NAMES[:2]),'master/acceptance/cost bytes unchanged')
    with(OUT/'apply.safe.json').open('x')as f:json.dump({'actualExit':0,'audit':result,'newAcceptedLeafDelta':0},f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'applied':True,'historicalAcceptedTasks':17,'currentCandidateSource':SOURCE,'acceptedLeafDelta':0}));return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['stage','apply']);raise SystemExit({'stage':stage,'apply':apply}[parser.parse_args().action]())
