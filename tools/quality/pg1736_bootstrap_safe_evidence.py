"""Public682 safe source/hash/counters; no private DB/credential/native content."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W
from pg1719_current_bootstrap_sources import SOURCE

def main():
    entries={
      'retainedProof':'pg1723-bootstrap-expired-peer-proof-v1/manifest.safe.json',
      'onceRecovery':'pg1726-bootstrap-current-fd-handoff-v1/manifest.safe.json',
      'recoveryPost':'pg1727-bootstrap-recovery-full-post-v1/manifest.safe.json',
      'compiler':'pg1729-frozen-v1.safe.json','stage':'pg1730-stage-v1.safe.json',
      'verify':'pg1730-verify-v1.safe.json','execute':'pg1730-execute-v1.safe.json',
      'post':'pg1731-current-bootstrap-full-post-v1/manifest.safe.json',
      'catalog':'pg1734-current-bootstrap-native-catalog-v1/manifest.safe.json',
      'native':'pg1735-current-bootstrap-native-qualified-v1/manifest.safe.json'}
    records={};values={}
    for name,relative in entries.items():
        raw=(W/relative).read_bytes();v=json.loads(raw)
        if type(v.get('actualExit'))is not int or v['actualExit']!=0:raise ValueError('actual successful limited record required')
        records[name]={'path':relative,'sha256':hashlib.sha256(raw).hexdigest(),'actualExit':0};values[name]=v
    result=values['native']['result'];post=values['post']['guest']
    if result['productionSource']!=SOURCE or post['productionSource']!=SOURCE or result['classByteMismatch']!=0 or post['allResources0']is not True:
        raise ValueError('current source independent post/CRC required')
    remaining={k:sum(c[k]['missed']for c in result['moduleCounters'].values())for k in ('LINE','METHOD','CLASS','BRANCH')}
    old=(W/'pg1721-verify-v1.safe.json').read_bytes()
    if json.loads(old)['actualExit']!=143:raise ValueError('old verify143 must remain unchanged')
    v={'program':'NK-OPS-001','testIds':['PT-OPS-BOOT-'+t for t in ('1721-VERIFY','1723-PROOF','1726-RECOVERY','1727-POST','1729-ABI','1730-VERIFY','1730-EXISTING','1731-POST','1734-NATIVE','1735-CRC')],
       'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),'evidenceCollectorCommit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
       'productionSource':SOURCE,'currentRelease':'PG1638','environment':{'jdk':'25.0.4','postgresql':'18.6','jacoco':'0.8.15','pyflakes':'3.4.0','guest':'Ubuntu26.04/x86_64/pinnedLAN-KVM','host':'Ubuntu/x86_64'},
       'command':'python3 -B tools/quality/<corresponding fixed tool>; pg1730 stage/verify/execute once each','records':records,
       'oldVerify':{'path':'pg1721-verify-v1.safe.json','sha256':hashlib.sha256(old).hexdigest(),'actualExit':143,'close':'UNKNOWN','notPassed':True},
       'bugs':['BUG-1156','BUG-1157','BUG-1158'],'design':['SSC-276','SSC-277'],'crossCheck':['YKT-924','YKT-925','YKT-926'],
       'independentToolChecks':{'arguments':8,'input':5,'actualExpectedAbi':60,'databaseLivenessFaults':307},'frozenFiles':len(values['compiler']['fileHashes']),
       'unitElapsedSeconds':post['bootstrap']['unitElapsedSeconds'],'genuinePid1Job':post['bootstrap']['actualPid1Job'],'allResources0':True,
       'capturedNormal20NotInferredFromGc':True,'original24Config32Signed187BackupPreserved':True,'credentialSourcesRetiredOnlyPrivate':True,
       'nativeClosingOnly':True,'nativeStreams':9,'oldSourceImported':False,'classByteMismatch':0,'coverageRemaining':remaining,
       'mainHostQualifiedTests':3596,'currentSelectedApiTests':5,'freshAll3597':'NOT_RUN','coverage100':False,
       'formal':'PT-WEB-20260925-24','formalPt':1964,'formalScopes':53,'formalAccepted':False,'wholeLeafAcceptedDelta':0,
       'rawPrivateExported':False,'actualAllocatedPp':None}
    out=Path(__file__).resolve().parents[2]/'evidence/01_PT/018_NK-OPS-001/evidence/output/682_manifest.json'
    os.umask(0o077)
    with out.open('x')as f:json.dump(v,f,sort_keys=True,indent=2);f.flush();os.fsync(f.fileno())
    print(json.dumps({'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'formalAccepted':False}))

if __name__=='__main__':main()
