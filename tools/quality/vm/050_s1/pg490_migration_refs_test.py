"""MIG202002/003: isolated pure negative matrix; never imports DBus/guest tool entrypoint."""
import ast, copy, hashlib, pathlib, stat

path=pathlib.Path(__file__).with_name('pg490_migration_refs.py')
parsed=ast.parse(path.read_text())
function=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='profile_only')
profile='/etc/schubert-nk/backup-profile.json'; root='/etc/schubert-nk'
env={'hashlib':hashlib,'pathlib':pathlib,'PROFILE':profile}
exec(compile(ast.Module(body=[function],type_ignores=[]),'<pure fixed profile delta>','exec'),env)
expected=b'fixed independent next profile'
item=lambda inode,mode,size,sha:{'metadata':[2,inode,0,999,mode,1,size,7,8],'sha256':sha}
before={root:{root:item(10,0o40750,4096,None),profile:item(11,0o100640,len(expected),'old'),root+'/other':item(12,0o100640,1,'unchanged')}}
after=copy.deepcopy(before); after[root][profile]=item(13,0o100640,len(expected),hashlib.sha256(expected).hexdigest())
after[root][root]['metadata'][7:]=[9,10]
assert env['profile_only'](before,after,expected);count=1
for name in [profile,root+'/other',root]:
 for field in ['sha256','metadata']:
  changed=copy.deepcopy(after)
  if field=='sha256':changed[root][name][field]='unexpected'
  else:changed[root][name][field][2]=88
  assert not env['profile_only'](before,changed,expected);count+=1
for index in [0,3,4,5,6]:
 changed=copy.deepcopy(after);changed[root][profile]['metadata'][index]+=1
 assert not env['profile_only'](before,changed,expected);count+=1
for changed in [{}, {root:{**after[root],root+'/extra':item(14,0o100640,1,'x')}}, {root:{profile:after[root][profile]}}]:
 assert not env['profile_only'](before,changed,expected);count+=1
assert not env['profile_only'](before,after,b'wrong expected');count+=1
print('PG490_PROFILE_ORACLE independentAssertions='+str(count)+' guestMutations0=true productionPT0=true')

security=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='profile_security')
env={'stat':stat};exec(compile(ast.Module(body=[security],type_ignores=[]),'<fixed security oracle>','exec'),env)
valid=[2,13,0,999,stat.S_IFREG|0o640,1,28,7,8]
assert env['profile_security'](valid,[],999);count=1
for attrs in [['system.posix_acl_access'],['system.posix_acl_default'],['system.posix_acl_access','user.comment']]:
 assert not env['profile_security'](valid,attrs,999);count+=1
for index,value in [(2,88),(3,88),(4,stat.S_IFREG|0o644),(4,stat.S_IFLNK|0o640),(5,2),(6,0),(6,4097)]:
 bad=valid.copy();bad[index]=value
 assert not env['profile_security'](bad,[],999);count+=1
for bad in [None,[],valid[:-1],valid+[1]]:
 assert not env['profile_security'](bad,[],999);count+=1
assert not env['profile_security'](valid,[],None);count+=1
for size in [1,4096]:
 good=valid.copy();good[6]=size;assert env['profile_security'](good,[],999);count+=1
print('PG490_SECURITY_ORACLE independentAssertions='+str(count)+' guestMutations0=true productionPT0=true')

execute=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='execute')
binding=next(n for n in execute.body if isinstance(n,ast.ClassDef) and n.name=='Binding')
env={'ast':ast};exec(compile(ast.Module(body=[binding],type_ignores=[]),'<fixed role binding>','exec'),env)
literal="a.application_name='PG480-fixed-recovery' and l.objsubid=1 and l.granted; usename in ('schubert_batch','schubert_api','schubert_web','schubert_inspector')"
actual=env['Binding']().visit(ast.Constant(literal)).value
assert "a.application_name='PG490-fixed-migration'" in actual
assert "l.mode='ExclusiveLock'" in actual
assert "('schubert_batch','schubert_app','schubert_web_session','schubert_inbox_inspector','schubert_backup')" in actual
assert all(name not in actual for name in ["'schubert_api'","'schubert_web'","'schubert_inspector'"])
assert env['Binding']().visit(ast.Constant('unrelated constant')).value=='unrelated constant'
print('PG490_ROLE_ORACLE independentAssertions=5 guestMutations0=true productionPT0=true')
