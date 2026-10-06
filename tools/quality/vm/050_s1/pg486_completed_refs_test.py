"""DONE485001..005 independent literal delta/epoch oracle; VM authority0."""
import ast,copy,hashlib,pathlib,re,stat,uuid
path=pathlib.Path(__file__).with_name('pg486_completed_refs.py');parsed=ast.parse(path.read_text())
names={'require','epoch_transition','changed_only'};defs=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(defs)==3
old='/opt/schubert-nk/releases/0.1.0-PG479';new='/opt/schubert-nk/releases/0.1.0-PG486';startup='/run/schubert-nk/startup';epoch=startup+'/epoch.current';config='/etc/schubert-nk';approval_path=config+'/release-approval/current'
env={'hashlib':hashlib,'re':re,'uuid':uuid,'stat':stat,'OLD':old,'NEXT':new,'STARTUP':startup,'EPOCH':epoch,'CONFIG':config,'APPROVAL':approval_path};exec(compile(ast.Module(body=defs,type_ignores=[]),str(path), 'exec'),env)
checks=0
def check(v):
 global checks
 checks+=1;assert v
def refused(call):
 global checks
 checks+=1
 try:call()
 except (ValueError,UnicodeError,TypeError):return
 raise AssertionError('invalid fixed vector accepted')
issued=b'NKEPOCH1\nstate=ISSUED\nboot_id=e07aa706-1acd-4e65-b309-d7f330f79d54\nepoch_id=11111111-2222-4333-8444-555555555555\nrun_id=49437eda-1681-43a9-883a-424eb55a6166\ncutoff_utc=2026-10-06T06:28:43.734078Z\nactivation_id=33333333-2222-4333-8444-555555555555\npermit_sha256='+b'3'*64+b'\n'
invalid=issued.replace(b'state=ISSUED',b'state=INVALID').replace(b'11111111-2222-4333-8444-555555555555',b'22222222-2222-4333-8444-555555555555').replace(b'permit_sha256='+b'3'*64,b'permit_sha256=-')
env['epoch_transition'](issued,invalid);check(True)
same_epoch=invalid.replace(b'epoch_id=22222222-2222-4333-8444-555555555555',b'epoch_id=11111111-2222-4333-8444-555555555555')
check(same_epoch.split(b'\n')[3]==issued.split(b'\n')[3])
fresh_other=invalid.replace(b'epoch_id=2222',b'epoch_id=1111')
check(fresh_other.split(b'\n')[3]!=issued.split(b'\n')[3]);env['epoch_transition'](issued,fresh_other);check(True)
for before,after in [(None,invalid),(issued,None),(issued,issued),(invalid,invalid),(issued,invalid[:-1]),(issued,b'\xff'),(issued,invalid+b'unknown=1\n'),(issued,invalid.replace(b'activation_id=3333',b'activation_id=4444')),(issued,invalid.replace(b'boot_id=e07aa',b'boot_id=f07aa')),(issued,same_epoch),(issued,invalid.replace(b'cutoff_utc=2026-10-06T06:28:43.734078Z',b'cutoff_utc=2026-10-06T06:28:43.734079Z')),(issued,invalid.replace(b'permit_sha256=-',b'permit_sha256='+b'2'*64)),(issued.replace(b'permit_sha256='+b'3'*64,b'permit_sha256=unknown'),invalid),(issued,invalid.replace(b'epoch_id=',b'foreign='))]:refused(lambda b=before,a=after:env['epoch_transition'](b,a))
approval=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG486\nmanifest_sha256='+b'2'*64+b'\n'
def material(raw,inode,mode):return {'metadata':[1,inode,0,0,stat.S_IFREG|mode,1,len(raw),10,11],'sha256':hashlib.sha256(raw).hexdigest()}
def directory(inode):return {'metadata':[1,inode,0,0,stat.S_IFDIR|0o700,2,4096,10,11],'sha256':None}
before={'current':old,'units':{'fixed-unit':{'MainPID':'0'}},'configuration':{'fixed-unit':{'User':'999'}},'unitFiles':{'fixed.service':material(b'fixed declaration',50,0o644)},'rows':{'table':[{'column':'synthetic'}]},'trees':{startup:{startup:directory(10),epoch:material(issued,11,0o600),startup+'/literal.permit':material(b'held original',12,0o600)},config:{config:directory(20),config+'/release-approval':directory(21),approval_path:material(b'old signed approval',22,0o400),config+'/private-api.env':material(b'synthetic protected config',23,0o600)},'/srv/schubert-nk/backup':{'saved.part':material(b'synthetic dump',30,0o600)},'/run/schubert-nk/pt-coverage':{'held.exec':material(b'synthetic old native',40,0o600)}}}
after=copy.deepcopy(before);after['current']=new;after['trees'][startup][epoch]=material(invalid,31,0o600);after['trees'][config][approval_path]=material(approval,32,0o400)
after['trees'][startup][startup]['metadata'][7:]=[30,31];after['trees'][config][config+'/release-approval']['metadata'][7:]=[30,31]
env['changed_only'](before,after,approval,issued,invalid);check(True)
for key in ['units','configuration','unitFiles','rows','current']:
 value=copy.deepcopy(after);value[key]={} if key!='current' else old;refused(lambda v=value:env['changed_only'](before,v,approval,issued,invalid))
for root,files in after['trees'].items():
 for name in files:
  value=copy.deepcopy(after);value['trees'][root][name]['sha256']='f'*64;refused(lambda v=value:env['changed_only'](before,v,approval,issued,invalid))
  value=copy.deepcopy(after);del value['trees'][root][name];refused(lambda v=value:env['changed_only'](before,v,approval,issued,invalid))
for name,root in [(epoch,startup),(approval_path,config)]:
 for index,value in [(0,2),(1,before['trees'][root][name]['metadata'][1]),(2,1),(3,1),(4,stat.S_IFREG|0o666),(5,2),(6,1)]:
  changed=copy.deepcopy(after);changed['trees'][root][name]['metadata'][index]=value;refused(lambda v=changed:env['changed_only'](before,v,approval,issued,invalid))
extra=copy.deepcopy(after);extra['trees'][startup]['unexpected.intent']=material(b'synthetic intent',90,0o600);refused(lambda:env['changed_only'](before,extra,approval,issued,invalid))
method=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='execute');calls=[n for n in ast.walk(method) if isinstance(n,ast.Call)]
# This witness may create private archive material, not start/stop/repair originals.
strings={n.value for n in ast.walk(parsed) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
check(not any(s in strings for s in ['start','stop','restart','daemon-reload','DELETE FROM','UPDATE schubert']))
check(any(isinstance(c.func,ast.Attribute) and c.func.attr=='RefUnit' for c in calls));check(any(isinstance(c.func,ast.Attribute) and c.func.attr=='UnrefUnit' for c in calls))
check('PG486-completed-codeonly' in path.read_text());check('old_epoch' in path.read_text());check('after.private.json' in strings)
print('PG486_COMPLETED_DELTA assertions='+str(checks)+' actual0=true authority0=true productionPT0=true')
