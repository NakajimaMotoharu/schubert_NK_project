"""MIG202002/003: isolated pure negative matrix; never imports DBus/guest tool entrypoint."""
import ast, copy, hashlib, pathlib

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
