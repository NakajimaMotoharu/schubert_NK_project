"""Independent manager declaration/history vectors; no systemctl or D-Bus."""
import ast,pathlib,re
tree=ast.parse(pathlib.Path(__file__).with_name('pg477_unit_references.py').read_text())
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['exec_record','after_exec','same_declaration','signed_declaration']]
assert len(nodes)==4
env={'re':re};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<fixed manager record>','exec'),env)
count=0
def check(value):
 global count
 count+=1
 if not value:raise AssertionError('independent manager record')
def record(path,argv,start='n/a',end='n/a',pid='0',code='(null)',status='0/0',ignore='no'):
 return '{ path='+path+' ; argv[]='+argv+' ; ignore_errors='+ignore+' ; start_time=['+start+'] ; stop_time=['+end+'] ; pid='+pid+' ; code='+code+' ; status='+status+' }'
plain=record('/usr/bin/caddy','/usr/bin/caddy run --config /etc/caddy/Caddyfile')
past=record('/usr/bin/caddy','/usr/bin/caddy run --config /etc/caddy/Caddyfile','Tue 2026-10-06 03:42:26 UTC','Tue 2026-10-06 03:52:46 UTC','3314130','exited','0')
check(env['exec_record'](plain)==('/usr/bin/caddy','/usr/bin/caddy run --config /etc/caddy/Caddyfile','no','n/a','n/a','0','(null)','0/0'))
check(env['after_exec'](plain));check(not env['after_exec'](past));check(env['same_declaration'](past,plain))
for changes in [{'start':'old'},{'end':'old'},{'pid':'1'},{'code':'exited'},{'status':'0'},{'status':'143'}]:
 check(not env['after_exec'](record('/usr/bin/caddy','/usr/bin/caddy',**changes)))
for bad in [None,'',plain+' '+plain,plain+'\n',plain.replace('ignore_errors=no','ignore_errors=unknown'),plain.replace('pid=0','pid=-1'),plain.replace('/usr/bin/caddy','relative'),plain.replace(' ; pid=0',' ; extra=0 ; pid=0'),'x'*65537]:
 check(env['exec_record'](bad) is None)
check(not env['same_declaration'](past,record('/usr/bin/caddy','/usr/bin/caddy run --config /foreign')))
morning='schubert-nk-morning-controller.service';inspector='schubert-nk-inbox-inspector.service';bootstrap='schubert-nk-bootstrap-admin.service'
argv='/usr/bin/java --enable-native-access=ALL-UNNAMED -cp fixed MorningProcessMain'
old=record('/usr/bin/java',argv+' --resume 31100027-2222-4333-8444-555555555555','old','old','1','exited','0')
new=record('/usr/bin/java',argv)
check(env['signed_declaration'](morning,old,new))
check(not env['signed_declaration'](morning,old,record('/usr/bin/java',argv+' --resume foreign')))
check(not env['signed_declaration'](morning,record('/usr/bin/java',argv),new))
prior='/opt/pgpt-tools-pg390/schubert-nk-inbox-inspector';target='/opt/schubert-nk/current/operations/bin/schubert-nk-inbox-inspector'
check(env['signed_declaration'](inspector,record(prior,prior),record(target,target)))
check(not env['signed_declaration'](inspector,record(prior,prior),record(target,target+' --extra')))
boot_argv='/usr/bin/java --enable-native-access=ALL-UNNAMED -cp fixed BootstrapAdminMain'
boot_new='/usr/bin/java --enable-native-access=ALL-UNNAMED -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=BOOTSTRAP-${INVOCATION_ID}-ordinary -cp fixed BootstrapAdminMain'
check(env['signed_declaration'](bootstrap,record('/usr/bin/java',boot_argv),record('/usr/bin/java',boot_new)))
check(not env['signed_declaration'](bootstrap,record('/usr/bin/java',boot_argv),record('/usr/bin/java',boot_new.replace('BOOTSTRAP-','API-'))))
check(not env['signed_declaration'](bootstrap,record('/usr/bin/java',boot_new),record('/usr/bin/java',boot_new)))
for unit in ['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service']:
 check(env['signed_declaration'](unit,past,plain))
 check(not env['signed_declaration'](unit,past,record('/usr/bin/caddy','/usr/bin/caddy --foreign')))
check(not env['signed_declaration'](morning,None,new));check(not env['signed_declaration'](bootstrap,past,None))
check(not env['signed_declaration'](None,past,plain));check(not env['signed_declaration']('foreign.service',past,plain))
print('PG477_EXEC_RECORD_TEST independentAssertions='+str(count)+' nativeMutation0=true productionPT0=true')
