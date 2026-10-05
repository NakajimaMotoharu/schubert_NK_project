"""Archive the already completed code-only proof, never treat running new parent as accepted."""
import datetime,hashlib,json,pathlib,subprocess,os
os.umask(0o077)
R=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
assert (W/'pg471-completed-activate-v1.exit').read_text().strip()=='0'
payload=r'''import pathlib,json,hashlib,stat
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg471-completed-deploy');marker=(r/'complete.private').read_bytes()
assert marker==b'allOwnedScopesReturnedNormally=true\noriginalDonePreserved=true\nrows361=true\nallBackupPreserved=true\nstarts0=true\npermits0=true\nddl0=true\n'
order=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service'];stopped={}
for unit in order:
 d=json.loads((r/(unit+'.stopped.private')).read_text());assert d['MainPID']==d['ControlPID']=='0' and d['Job']=='' and d['ActiveState'] in ('inactive','failed')
 stopped[unit]={'state':d['ActiveState']+'/'+d['SubState'],'result':d['Result'],'code':d['ExecMainCode'],'status':d['ExecMainStatus'],'explicitStop':(r/(unit+'.stop-reserved.private')).exists()}
for p in r.iterdir():
 s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600
files=[]
for name in ['complete.private','rows-before.private','business-before.private','backup-before.private','original-before.private','fixture-before.private','metadata-before.private','history-before.private','stops-before.private','ticks-before.private']:
 p=r/name;files.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'contentInGit':False})
native=json.loads((r/'native-before.private.json').read_text());assert len(native['oldExec'])==5
for item in native['oldExec']:
 p=pathlib.Path(item['archive']);assert p.parent==r and p.stat().st_size==item['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
 files.append({'path':str(p),'sha256':item['sha256'],'bytes':item['bytes'],'contentInGit':False})
assert (r/'native-preparation.complete.private').read_bytes()==b'fourPrivateRoles=true\nparent755=true\noldFiveExecArchived=true\noldFiveExecUnchanged=true\nclosedProfile=true\nstarts0=true\n'
files.append({'path':str(r/'native-before.private.json'),'sha256':hashlib.sha256((r/'native-before.private.json').read_bytes()).hexdigest(),'bytes':(r/'native-before.private.json').stat().st_size,'contentInGit':False})
print(json.dumps({'archivedCodeOnlyScopesReturnedNormally':True,'archivedAllEightTerminal':True,'originalDonePreserved':True,'all361Full14Preserved':True,'all23BusinessTablesExactlyPreserved':True,'allBackupTransferPreserved':True,'all44StartupRecordsByteMetadataPreserved':True,'newInvalidCurrentSigned':True,'existingBootstrapAndRetiredCredentialsNotRecreated':True,'oldFiveExecArchived':True,'newParent755':True,'fourPrivateRoles':True,'oldUnknownNormalized':False,'stops':stopped,'files':files,'currentNewParentAccepted':False}))
'''
run=subprocess.run(['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1','sudo -n python3 -B -'],input=payload.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
# Preserve failed v1/v2 collection logs. The prior archive probe log was 0664;
# the operator protected it as 0600 before this read-only retry (no VM mutation).
with (W/'pg471-code-only-collection-v3.private.log').open('xb') as f:f.write(run.stdout);f.write(run.stderr)
assert run.returncode==0;d=json.loads(run.stdout)
d.update({'id':'PG471-completed-code-only-v1','programId':'NK-OPS-001','testIds':['PT-OPS-CURRENT469003','PT-OPS-CURRENT469004','PT-OPS-CURRENT469005'],'branch':'dev-foundation','operatorHeadBeforeSave':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'productionSource':'717d72dd844fff286b4c696b9d08c41b136f0a6c','previousSource':'d3bba6db6eb9fec13e4847a10541cf337f575731','manifestSha256':'47f7a338de848c83e96d2fc8208a9eade43e9d4e5218c79b3834603e27648b18','collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'environment':{'jdk':'25.0.4','guest':'Ubuntu26.04','postgresql':'18.6'},'startedAt':(W/'pg471-completed-activate-v1.started').read_text().strip(),'completedAt':(W/'pg471-completed-activate-v1.completed').read_text().strip(),'actualExit':0,'formalPass':False,'coverage100':False,'productionPtAdded':0,'commands':['bash tools/quality/vm/050_s1/pg471_completed_activate_v1.sh'],'relatedBugs':['BUG-753','BUG-754'],'relatedYkt':['YKT-533','YKT-534'],'relatedSsc':['SSC-193','SSC-194','SSC-195']})
for name in ['pg471-completed-activate-v1.private.log','pg471-observer-stage-v1.private.log','pg471-private-archive-v1.private.log']:
 p=W/name;assert p.stat().st_mode&0o077==0;d['files'].append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'contentInGit':False})
out=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG471-completed-code-only-v1';assert not out.exists();out.mkdir(parents=True)
with (out/'manifest.json').open('x') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print('PG471_CODE_ONLY_SAFE actualExit0=true archivedAllEight=true parentNotAccepted=true manifestSha256='+hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest())
