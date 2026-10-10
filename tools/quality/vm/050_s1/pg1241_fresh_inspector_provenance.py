"""Independent real Inspector first-new-day receipts and zero eligible-row oracle.

SS32412.3/12.7,V010/012/019,SS343/353; not whole parent/native100.
"""
import inspect
import pg1222_completed_retirement_preflight as transport

PAYLOAD=r'''
import pathlib,json,hashlib,datetime,subprocess,stat,os,pwd
os.umask(0o077)
def require(ok):
 if not ok:raise ValueError('fresh same-root Inspector provenance refused')
BOOT='cbca8738-3b24-4090-b77c-bf029677cdd6';RUN='9f651096-aef9-4fba-90b0-a653e99f035a';CUT='2026-10-10T20:03:22.718197Z';INV='99c487c7c9444c81bf20813d03875565'
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
base=pathlib.Path('/var/lib/pgpt-s1-preservation');save=base/'pg1241-fresh-inspector-provenance-v1';require(not os.path.lexists(save))
before_raw=(base/'pg1238-fresh-day-ordinary-before-v1/before.private.json').read_bytes();require(hashlib.sha256(before_raw).hexdigest()=='57a5889403d752e2558f144b41e9ddd702451d78bf0deab5b6f2fd462b02966e');before=json.loads(before_raw)
anchor=('NKRUN1\n'+RUN+'\n'+CUT+'\n').encode();require(pathlib.Path('/var/lib/schubert-nk/maintenance/runs',RUN+'.run').read_bytes()==anchor)
manifest=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()=='0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d'and json.loads(manifest)['source']['commit']=='d5b00104280028d9ea81b44c1d1c805f3c2861ed')
def eligible_rows(rows,cut):
 require(type(rows)is list and isinstance(cut,datetime.datetime)and cut.tzinfo is not None)
 result=[]
 for row in rows:
  require(type(row)is dict and row.get('processing_state')in ['PROCESSING','COMPLETED','ERROR']and type(row.get('expires_at'))is str)
  expiry=datetime.datetime.fromisoformat(row['expires_at']);require(expiry.tzinfo is not None)
  if row['processing_state']in ['COMPLETED','ERROR']and expiry<cut:result.append(row)
 return result
cut=datetime.datetime.fromisoformat(CUT.replace('Z','+00:00'));eligible=eligible_rows(before['current']['rows']['schubert.request_inbox'],cut)
require(len(eligible)==0) # This fixture only. Future nonempty candidates require full cipher/reference oracle.
def command(args):
 r=subprocess.run(args,capture_output=True,timeout=15);require(r.returncode==0 and len(r.stdout)<=8388608);return r.stdout
def observed():
 q="begin isolation level repeatable read read only;set local timezone='UTC';select coalesce(jsonb_agg(to_jsonb(t)order by to_jsonb(t)::text),'[]'::jsonb)from schubert.request_inbox t;select to_jsonb(t)from schubert.inbox_inspection_progress t where run_id='"+RUN+"';select to_jsonb(t)from schubert.batch_runs t where run_id='"+RUN+"'and step='CLEAN_INBOX_OUTBOX';commit;"
 values=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines();require(len(values)==3);rows,progress,step=map(json.loads,values)
 require(rows==before['current']['rows']['schubert.request_inbox'])
 require(progress['run_id']==RUN and datetime.datetime.fromisoformat(progress['cutoff'])==cut and progress['after_message_id']is None and progress['completed_at']is not None)
 require(all(type(progress[k])is int and progress[k]==0 for k in ['inspected_count','deleted_count','protected_count']))
 require(step['run_id']==RUN and step['business_date']=='2026-10-11'and step['status']=='SUCCESS'and step['error_code']is None and all(type(step[k])is int and step[k]==0 for k in ['target_count','success_count','failure_count','byte_count']))
 return{'progress':progress,'step':step,'inboxRows':rows}
current=observed();require(current==observed())
unit='schubert-nk-inbox-inspector.service';journal=command(['journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT='+unit,'INVOCATION_ID='+INV,'-o','json','--no-pager']);records=[json.loads(x)for x in journal.splitlines()]
require(len(records)==5 and all(v.get('_BOOT_ID')==BOOT.replace('-','')and v.get('_PID')=='1'and v.get('_UID')=='0'and v.get('UNIT')==unit and v.get('INVOCATION_ID')==INV for v in records))
def one(mid,kind,job,result):
 matches=[v for v in records if v.get('MESSAGE_ID')==mid and v.get('JOB_TYPE')==kind and v.get('JOB_ID')==job and(result is None or v.get('JOB_RESULT')==result)];require(len(matches)==1);return matches[0]
start=one('7d4958e842da4a758f6c1cdc7b36dcc5','start','101554',None);done=one('39f53479d3a045ac8e11786248231fbf','start','101554','done');stop=one('9d1aaa27d60140bd96365438aad20286','stop','101701','done')
require(61234139496<int(start['__MONOTONIC_TIMESTAMP'])<int(done['__MONOTONIC_TIMESTAMP'])<int(stop['__MONOTONIC_TIMESTAMP'])<63034139496)
identity=pwd.getpwnam('schubert-inbox-inspector');copies=[]
for suffix,digest in [('terminal.exec','330c868ea20828a2fff3666a6cbedd77f06fcf30095d7de711412ce47183025f'),('closing.exec','47910f38118892b0c7618714514a0017ee51d1549e3eb9d37ab339b6606daae6')]:
 p=pathlib.Path('/run/schubert-nk/pt-coverage/ordinary-inspector196')/(INV+'.'+suffix);m=p.lstat();b=p.read_bytes()
 now=p.lstat();metadata=lambda s:(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 require(stat.S_ISREG(m.st_mode)and(m.st_uid,m.st_gid,stat.S_IMODE(m.st_mode),m.st_nlink)==(identity.pw_uid,identity.pw_gid,0o600,1)and len(b)==17228 and hashlib.sha256(b).hexdigest()==digest and metadata(now)==metadata(m)and not os.listxattr(p))
 require(str(p)not in before['native']);copies.append((suffix,b,digest))
save.mkdir(mode=0o700)
def persist(name,data):
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
persist('pid1.private.jsonl',journal);persist('database.private.json',json.dumps(current,sort_keys=True).encode())
for name,b,digest in copies:persist(name,b)
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'run':'PG1241-fresh-inspector-provenance-v1','productionSource':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','actualExit':0,'genuinePid1StartDoneStop':True,'currentInspectorNativeStreamsPreserved':2,'nativeBytes':34456,'priorInboxRows':len(before['current']['rows']['schubert.request_inbox']),'independentEligibleRows':0,'expectedActualCounts':[0,0,0],'inboxRowsUnchanged':True,'newRunCutoffProgressCompleted':True,'sameRunInboxStepSuccess':True,'journalSha256':hashlib.sha256(journal).hexdigest(),'normalGcNotCompletionProof':True,'sqlWrites0':True,'classSessionCounterQualificationPending':True,'parentWholeAccepted':False,'formalAccepted':False,'rawExported':False}))
'''

def main():
    compile(PAYLOAD,'<actual Inspector provenance>','exec')
    entry=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1241-fresh-inspector-provenance-v1')
    env=dict(transport.__dict__);env['payload']=lambda:PAYLOAD
    exec(compile(entry,'<new-only actual Inspector provenance transport>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
