"""Collect only nonsecret flags, hash and process metadata. No raw private payload to Git."""
import datetime,hashlib,json,os,pathlib,subprocess
R=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
payload=r'''import pathlib,json,hashlib,os,stat
assert os.geteuid()==0
roots={'handoff':'/var/lib/pgpt-s1-preservation/pg497-owned-tool-handoff-v1','invalidation':'/var/lib/pgpt-s1-preservation/pg497-canonical-invalidation-v1'}
result={}
for scope,root in roots.items():
 p=pathlib.Path(root);files={}
 for f in p.iterdir():
  if f.is_file():
   s=f.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
   files[f.name]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':s.st_size,'mode':'0600','owner':'Root'}
 result[scope]={'privateFiles':files}
result['handoff']['safeFlags']=json.loads(pathlib.Path(roots['handoff'],'complete.private.json').read_text())
result['invalidation']['safeFlags']=pathlib.Path(roots['invalidation'],'complete.private').read_text().splitlines()
print(json.dumps(result,sort_keys=True))
'''
raw=subprocess.check_output(ssh+['sudo -n python3 -B -'],input=payload.encode());private=json.loads(raw)
for phase,expected in [('pg496-recover-native-v1',143),('pg497-handoff-native-v2',0),('pg497-invalidation-verify-v1',0),('pg497-invalidation-native-v1',0)]:assert int((W/(phase+'.exit')).read_text())==expected
manifest={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'program':'NK-OPS-001','testIDs':['REC204001','REC204002','REC204003','REC204004','REC205001'],
 'productionSource':'38899a05b5c2daeecfc5af8ea5ae748e29954c60','testedUnactivatedCandidate':'a2e98ce9e96c42425921e3686e8ae7a94bff9e6c','operatorCheckpoint':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip(),
 'branch':'dev-foundation','OS':'Ubuntu 26.04 guest','JDK':'25.0.4','hostToolAssertions':{'PG496Java':88,'PG496Python':134,'PG497HandoffPython':72,'PG497InvalidationJava':88},
 'actualExits':{'PG496-recover-v1':143,'PG497-handoff-v1-refusal':1,'PG497-handoff-v2':0,'PG497-invalidation-verify-v1':0,'PG497-invalidation-native-v1':0},
 'coverage':{'productionCredit':False,'global100':False,'nativeCoverageAccepted':False},'formalAccepted':False,'oldCloseNotInferred':True,'ITSTAccepted':False,
 'BUG':['799','802','803','804','805','806'],'SSC':['204','205'],'YKT':['570','571','572','573','574','575'],'privateEvidence':private,
 'postconditions':{'currentSameEpochInvalid':True,'intentRetirements':0,'starts':0,'all24RowsAndOriginalValuesUnchanged':True,'allTenKernelEmpty':True,'allNewInvalidationScopesReturnedNormally':True}}
out=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG497-timeout-handoff-invalidation-v1';assert not out.exists();out.mkdir(parents=True)
with (out/'manifest.json').open('x') as f:json.dump(manifest,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
print('PG497_SAFE_MANIFEST sha256='+hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest()+' rawPrivateIncluded=false formalAccepted=false')
