"""Publish only bounded safe cold proof, never raw DB/native/credential files."""
import hashlib
import json
from pathlib import Path
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private/pg1000-cold-overlay-v1')
ROOT=Path(__file__).resolve().parents[4]

if __name__=='__main__':
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG996-1005-current-cold-v1'
    assert not out.exists();out.mkdir(parents=True)
    paths={'cow':P/'manifest.safe.json','boot':P/'boot-result.safe.json',
      'cold':W/'pg1004-cold-readonly-v3/manifest.safe.json','configuration':W/'pg1005-cold-configuration-v1/manifest.safe.json'}
    data={k:json.loads(p.read_bytes())for k,p in paths.items()}
    assert data['cold']['actualExit']==data['configuration']['actualExit']==0
    result={'run':'PG996-1005-current-cold-v1','source':'40ef6e894573d2ffab1d1732124960f9c98d5f97',
      'boot':'cbca8738-3b24-4090-b77c-bf029677cdd6','sourceEvidenceSha256':{k:hashlib.sha256(p.read_bytes()).hexdigest()for k,p in paths.items()},
      'cow':{k:data['cow'][k]for k in ['actualExit','logicalCompareExit','workingDiskBytes','originalDiskUnchanged','originalInternalSnapshotPreserved','standaloneBackup']},
      'bootObservation':data['boot'],'coldObservation':data['cold'],'configurationObservation':data['configuration'],
      'failedAttempts':[{'run':'PG997-v1','actualExit':1,'convertCode':None,'reason':'capacity refusal; code missing BUG1003'},
                        {'run':'PG997-v2','actualExit':1,'convertCode':1,'reason':'5GiB capacity refusal, durable failure receipt'},
                        {'run':'PG1002-v1','actualExit':1,'reason':'BUG1004 typed-empty capture bypass'},
                        {'run':'PG1003-v2','actualExit':1,'reason':'BUG1005 UnitRef lifetime omitted'}],
      'failureArtifactsPreserved':True,'rawExported':False,'productionPtAdded':0,'nativeAdded':0,
      'currentNativeRemaining':{'LINE':903,'METHOD':176,'CLASS':12,'BRANCH':733},
      'formal':'PT-WEB-20260925-24/1964PT/53scope','formalAccepted':False,'wholeWbsAcceptedDelta':0,
      'designSourceCommit':'8f1b5852c4ec481999b2c8de4112661adb576e83',
      'designMainMergeCommit':'57108ee17a23795cfb94edafb9191c7e8a5ae82e',
      'designPr':'https://github.com/NakajimaMotoharu/schubert_NK_project/pull/80',
      'unaccepted':['SSC243 empty cold namespace/hostRO preparation','Inspector current native/new-day lawful route','remaining PGPT/formal gates']}
    with(out/'manifest.json').open('x')as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'run':result['run'],'manifestSha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'wholeAcceptedDelta':0}))
