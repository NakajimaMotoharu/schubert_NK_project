"""One readonly post-maintenance all-column snapshot; never business actions."""
import hashlib,os,pathlib,subprocess
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent;W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1']
payload=r'''
import datetime,hashlib,importlib.util,json,os,pathlib,subprocess,time
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
base=pathlib.Path('/var/lib/pgpt-s1-preservation/pg605-fresh-parent-v2');raw=(base/'before.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='f6b3a93a9ad83396098fea7bbabef6fb03ca47b5e9a0e4e4bac0902f7b5ad8be'
old=json.loads(raw);sealed=json.loads((base/'cleanup-oracle.private.json').read_bytes());assert sealed['source']==old['source']=='23b14a44b10504172e030bbd6625926bf049fb5c'
path=pathlib.Path('/var/lib/pgpt-s1-preservation/pg553-oracle-tools-v3/pg478_cleanup_oracle.py');spec=importlib.util.spec_from_file_location('independent',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg610-preui-v1');assert not root.exists()
def manager(unit):
 raw=subprocess.check_output(['/usr/bin/systemctl','show',unit,'--property=MainPID,ControlPID,Job,InvocationID,ActiveState,SubState,Result,ExecMainCode,ExecMainStatus'],text=True,timeout=5)
 return dict(s.split('=',1)for s in raw.splitlines())
def parent():
 p=manager('schubert-nk-morning-controller.service');assert p['MainPID']=='1207482' and p['InvocationID']=='5a1acaa0c35e484c979401e3b6dfb36a' and p['Job']=='87863';return p
def preui():
 for u in ['schubert-nk-api.service','schubert-nk-web.service','caddy.service']:
  p=manager(u);assert p['MainPID']==p['ControlPID']=='0' and not p['Job']
deadline=86264628081/1e6+1800
while time.monotonic()<deadline:
 p=parent();preui()
 c=manager('schubert-nk-cleanup.service');e=manager('schubert-nk-expiry-cleanup.service')
 if c['InvocationID']!=old['units']['schubert-nk-cleanup.service']['InvocationID'] and e['InvocationID']!=old['units']['schubert-nk-expiry-cleanup.service']['InvocationID'] and all(v['MainPID']==v['ControlPID']=='0' and not v['Job'] and v['Result']=='success' and v['ExecMainCode']=='1' and v['ExecMainStatus']=='0'for v in(c,e)):break
 time.sleep(.1)
else:raise ValueError('preui capture timed out')
act=pathlib.Path('/var/lib/schubert-nk/maintenance/active').read_text().splitlines();assert len(act)==4 and act[0]=='NKACT1';run,cutoff,activation=act[1:]
assert m.instant(old['bounds']['lower'])<=m.instant(cutoff)<=m.instant(old['bounds']['upper'])
expected=m.candidates(old['rows'],cutoff);assert expected['inbox_scan_candidates']==sealed['expected']['inbox_scan_candidates']
oracle={'expected':expected,'inboxExpectedDeleted':sealed['expected']['inbox_scan_candidates']}
q="begin isolation level repeatable read read only;set local timezone='UTC';"
for t in old['rows']:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
q+='commit;';raw=subprocess.check_output(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],timeout=30);assert len(raw)<=33554432
new={}
for line in raw.splitlines():
 v=json.loads(line);assert v['table']not in new;new[v['table']]=v['rows']
assert parent()==p;preui();env={};exec(compile(EVALUATOR,'<independent survivors>','exec'),env);summary=env['evaluate'](old['rows'],new,oracle,run)
root.mkdir(mode=0o700)
value={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':old['source'],'run':run,'cutoff':cutoff,'activation':activation,'rows':new,'expected':expected,'summary':summary,'parent':p,'parentAccepted':False,'newGeneratedRowsAccepted':False}
with(root/'full-rows.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
for d in(root,root.parent):
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'all24IndependentSurvivorsEqual':True,'oldBatchPreserved':summary['schubert.batch_runs']['oldPreserved'],'authDeleted':summary['schubert.auth_sessions']['deleted'],'httpDeleted':summary['schubert_web_session.web_http_sessions']['deleted'],'inboxDeleted':summary['schubert.request_inbox']['deleted'],'loginIpDeleted':summary['schubert.login_ip_attempts']['deleted'],'snapshotSha256':hashlib.sha256((root/'full-rows.private.json').read_bytes()).hexdigest(),'parentAccepted':False}))
'''
log=W/'pg610-preui-v1.private.log';assert not log.exists()
with log.open('xb')as f:
 result=subprocess.run(ssh+['sudo -n python3 -B -'],input=('EVALUATOR='+repr((R/'pg555_cleanup_postcondition.py').read_text())+'\n'+payload).encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
with(W/'pg610-preui-v1.exit').open('x')as f:f.write(str(result.returncode)+'\n')
print('PG610_PREUI actualExit='+str(result.returncode)+' privateLogSha256='+hashlib.sha256(log.read_bytes()).hexdigest());raise SystemExit(result.returncode)
