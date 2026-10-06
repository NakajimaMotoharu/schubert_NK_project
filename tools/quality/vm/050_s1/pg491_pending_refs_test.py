"""MIG202008 independent exact publication delta oracle, no guest access."""
import ast,copy,hashlib,pathlib,stat
parsed=ast.parse(pathlib.Path(__file__).with_name('pg491_pending_refs.py').read_text())
names={'APPROVAL','NEW_APPROVAL'}
nodes=[n for n in parsed.body if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in names for t in n.targets)]
nodes.append(next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='approval_only'))
env={'hashlib':hashlib,'pathlib':pathlib,'stat':stat};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<pure publication delta>','exec'),env)
root='/etc/schubert-nk';folder=root+'/release-approval';file=folder+'/current'
new=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG489\nmanifest_sha256=652a5e4a31dd9251c5a89cb4f5dea031f157b17ab58f466fb329cdcbfbe1be1c\n'
assert env['NEW_APPROVAL']==new
def item(inode,mode,size,digest):return {'metadata':[2,inode,0,0,mode,1,size,7,8],'sha256':digest}
old={root:{folder:item(10,0o40700,4096,None),file:item(11,0o100400,len(new),'old'),root+'/backup-profile.json':item(12,0o100640,100,'profile028')}}
after=copy.deepcopy(old);after[root][file]=item(13,0o100400,len(new),hashlib.sha256(new).hexdigest());after[root][folder]['metadata'][7:]=[9,10]
assert env['approval_only'](old,after);count=2
for name in [file,folder,root+'/backup-profile.json']:
 for field in ['sha256','metadata']:
  changed=copy.deepcopy(after)
  if field=='sha256':changed[root][name][field]='foreign'
  else:changed[root][name][field][2]=99
  assert not env['approval_only'](old,changed);count+=1
for index in [0,3,4,5,6]:
 changed=copy.deepcopy(after);changed[root][file]['metadata'][index]+=1
 assert not env['approval_only'](old,changed);count+=1
for changed in [{},{root:{**after[root],root+'/extra':item(14,0o100400,1,'extra')}},{root:{file:after[root][file]}}]:
 assert not env['approval_only'](old,changed);count+=1
print('PG491_APPROVAL_ORACLE independentAssertions='+str(count)+' guestMutations0=true')
