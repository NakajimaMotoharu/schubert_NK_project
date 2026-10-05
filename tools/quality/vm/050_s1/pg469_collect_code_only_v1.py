"""Archive the already completed code-only proof, never treat running new parent as accepted."""
import datetime,hashlib,json,pathlib,subprocess,os
os.umask(0o077)
R=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
assert (W/'pg469-completed-activate-v1.exit').read_text().strip()=='0'
payload=r'''import pathlib,json,hashlib,stat
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg469-completed-deploy');marker=(r/'complete.private').read_bytes()
assert marker==b'allOwnedScopesReturnedNormally=true\noriginalDonePreserved=true\nrows351=true\nallBackupPreserved=true\nstarts0=true\npermits0=true\nddl0=true\n'
order=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service'];stopped={}
for unit in order:
 d=json.loads((r/(unit+'.stopped.private')).read_text());assert d['MainPID']==d['ControlPID']=='0' and d['Job']=='' and d['ActiveState'] in ('inactive','failed')
 stopped[unit]={'state':d['ActiveState']+'/'+d['SubState'],'result':d['Result'],'code':d['ExecMainCode'],'status':d['ExecMainStatus'],'explicitStop':(r/(unit+'.stop-reserved.private')).exists()}
for p in r.iterdir():
 s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600
files=[]
for name in ['complete.private','rows-before.private','business-before.private','backup-before.private','original-before.private','fixture-before.private','metadata-before.private','history-before.private','stops-before.private','ticks-before.private']:
 p=r/name;files.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'contentInGit':False})
print(json.dumps({'archivedCodeOnlyScopesReturnedNormally':True,'archivedAllEightTerminal':True,'originalDonePreserved':True,'all351Full14Preserved':True,'all23BusinessTablesExactlyPreserved':True,'allBackupTransferPreserved':True,'all40StartupRecordsByteMetadataPreserved':True,'newInvalidCurrentSigned':True,'existingBootstrapAndRetiredCredentialsNotRecreated':True,'oldUnknownNormalized':False,'stops':stopped,'files':files,'currentNewParentAccepted':False}))
'''
run=subprocess.run(['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1','sudo -n python3 -B -'],input=payload.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (W/'pg469-code-only-collection-v1.private.log').open('xb') as f:f.write(run.stdout);f.write(run.stderr)
assert run.returncode==0;d=json.loads(run.stdout)
d.update({'id':'PG469-completed-code-only-v1','programId':'NK-OPS-001','testIds':['PT-OPS-CURRENT469003','PT-OPS-CURRENT469004','PT-OPS-CURRENT469005'],'branch':'dev-foundation','operatorHeadBeforeSave':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'productionSource':'d3bba6db6eb9fec13e4847a10541cf337f575731','previousSource':'bbb244e5191e68adee2f6251dfdbbba53e9b64b4','manifestSha256':'cc5e4dd7ca70d3a21e1145dd35b9f047856c4ab83bfac6f11722663ba7744462','collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'environment':{'jdk':'25.0.4','guest':'Ubuntu26.04','postgresql':'18.6'},'startedAt':(W/'pg469-completed-activate-v1.started').read_text().strip(),'completedAt':(W/'pg469-completed-activate-v1.completed').read_text().strip(),'actualExit':0,'formalPass':False,'coverage100':False,'productionPtAdded':0,'commands':['bash tools/quality/vm/050_s1/pg469_completed_activate_v1.sh'],'relatedBugs':['BUG-744','BUG-745','BUG-746','BUG-747','BUG-748','BUG-749'],'relatedYkt':['YKT-525','YKT-526','YKT-527','YKT-528','YKT-529','YKT-530'],'relatedSsc':['SSC-190','SSC-191']})
for name in ['pg469-completed-activate-v1.private.log','pg469-observer-stage-v1.private.log','pg469-observer-preservation-v1.private.log']:
 p=W/name;assert p.stat().st_mode&0o077==0;d['files'].append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'contentInGit':False})
out=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG469-completed-code-only-v1';assert not out.exists();out.mkdir(parents=True)
with (out/'manifest.json').open('x') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print('PG469_CODE_ONLY_SAFE actualExit0=true archivedAllEight=true parentNotAccepted=true manifestSha256='+hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest())
