"""BREC198010 independent full-value/config delta oracle; no guest authority."""
import ast,copy,hashlib,pathlib,stat
source=pathlib.Path(__file__).with_name('pg481_pending_refs.py');tree=ast.parse(source.read_text())
names=['require','configuration_changed_only_approval','compare']
defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
approval=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG479\nmanifest_sha256=a1c34cddba7d02cc479ccbe311a7ef7210f31f8aa1070f7685a2985d5503f286\n'
root='/etc/schubert-nk/release-approval';path=root+'/current'
env={'hashlib':hashlib,'stat':stat,'pathlib':pathlib,'APPROVAL':path,'APPROVAL_ROOT':root,'NEW_APPROVAL':approval}
exec(compile(ast.Module(body=defs,type_ignores=[]),str(source),'exec'),env)
n=0
def check(value):
 global n
 assert value;n+=1
def refused(value):
 global n
 try:env['compare'](value,True)
 except ValueError:n+=1;return
 raise AssertionError('changed protected value accepted')
old={root:{'metadata':[1,2,0,0,stat.S_IFDIR|0o700,2,4096,10,11],'sha256':None},path:{'metadata':[1,3,0,0,stat.S_IFREG|0o400,1,120,10,11],'sha256':'0'*64},'/etc/schubert-nk/private-api.env':{'metadata':[1,4,0,0,stat.S_IFREG|0o600,1,40,10,11],'sha256':'1'*64}}
new=copy.deepcopy(old);new[path]={'metadata':[1,5,0,0,stat.S_IFREG|0o400,1,len(approval),30,31],'sha256':hashlib.sha256(approval).hexdigest()};new[root]['metadata'][7:]=[30,31]
check(env['configuration_changed_only_approval'](old,new))
for index,value in [(2,1),(3,986),(4,stat.S_IFREG|0o600),(5,2),(6,len(approval)+1)]:
 bad=copy.deepcopy(new);bad[path]['metadata'][index]=value;check(not env['configuration_changed_only_approval'](old,bad))
for key in list(new):
 bad=copy.deepcopy(new);bad[key]['sha256']='f'*64;check(not env['configuration_changed_only_approval'](old,bad))
for index in range(7):
 bad=copy.deepcopy(new);bad[root]['metadata'][index]+=1;check(not env['configuration_changed_only_approval'](old,bad))
for key in list(old):
 bad=copy.deepcopy(new);del bad[key];check(not env['configuration_changed_only_approval'](old,bad))
bad=copy.deepcopy(new);bad['foreign']=copy.deepcopy(new[path]);check(not env['configuration_changed_only_approval'](old,bad))
protected={'units':{'MainPID':'0','result':'timeout'},'configuration':{'hardening':'fixed'},'rows':{'pending':[{'status':'RUNNING','ended':None}]},'original':{'run':'49437eda','cutoff':'734078'},'backup':{'part':'dump-only'},'transfer':{'old':[]},'startup':{'epoch':'INVALID'},'native':{'parent':'hash'},'request':{'sha':'old'},'config':old}
env['before']=copy.deepcopy(protected);actual=copy.deepcopy(protected);actual['config']=new;env['strict']=lambda *a:approval
env['compare'](actual,True);check(True)
env['compare'](copy.deepcopy(protected),False);check(True)
for key in protected:
 if key=='config':continue
 bad=copy.deepcopy(actual);bad[key]={'foreign':True};refused(bad)
bad=copy.deepcopy(actual);bad['extra']=True;refused(bad)
env['strict']=lambda *a:b'foreign';refused(actual)
pin=next(x for x in tree.body if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id=='WITNESS_SHA').value.value
check(hashlib.sha256(source.with_name('pg480_backup_refs.py').read_bytes()).hexdigest()==pin)
binding=next(x for x in ast.walk(tree) if isinstance(x,ast.ClassDef) and x.name=='FixedBinding')
bindenv={'ast':ast,'BEFORE':'/opt/schubert-nk/releases/0.1.0-PG477'};exec(compile(ast.Module(body=[binding],type_ignores=[]),'<binding>','exec'),bindenv)
fixture=ast.parse("x=b'Pg480BackupRecovery';y='/opt/schubert-nk/releases/0.1.0-PG477';z=\"a.application_name='PG480-fixed-recovery'\";keep='PG480-observer'\n")
bound=bindenv['FixedBinding']().visit(fixture);ast.fix_missing_locations(bound);result={'selectedRelease':'fixed-new'};exec(compile(bound,'<fixture>','exec'),result)
check(result['x']==b'Pg481PendingDeployment');check(result['y']=='fixed-new');check(result['z']=="a.application_name='PG481-fixed-pending'");check(result['keep']=='PG480-observer')
print('PG481_PENDING_ORACLE assertions='+str(n)+' actual0=true vmAuthority0=true')
