"""Independent literal SS names, effective-unit join, owner/mode/ACL/null vectors."""
import copy,pathlib,stat
import pg506_native_namespace_contract as contract

n=0
def check(value,expected):
 global n
 assert value is expected;n+=1
# Fixed literal approved names, not obtained from the implementation's catalog.
gold={'parent','backup','cleanup','expiry','inspector','root-api','root-web','ordinary-api','ordinary-web',
 'root-api193','root-web193','ordinary-api193','ordinary-web193','ordinary-inspector196','ordinary-bootstrap196'}
check(contract.catalog(gold),True)
for name in gold:check(contract.catalog(gold-{name}),False)
for value in [None,list(gold),gold|{'foreign'},set()]:check(contract.catalog(value),False)
units={'schubert-nk-api.service':{'root-api193','ordinary-api193'},
 'schubert-nk-web.service':{'root-web193','ordinary-web193'},
 'schubert-nk-inbox-inspector.service':{'ordinary-inspector196'},
 'schubert-nk-bootstrap-admin.service':{'ordinary-bootstrap196'}}
check(contract.effective_roles(units),True)
for name in units:
 bad=copy.deepcopy(units);del bad[name];check(contract.effective_roles(bad),False)
 bad=copy.deepcopy(units);bad[name]={'foreign'};check(contract.effective_roles(bad),False)
check(contract.effective_roles(None),False)
for name,uid,gid in [('root-api193',0,0),('root-web193',0,0),('ordinary-api193',999,999),
 ('ordinary-web193',997,997),('ordinary-inspector196',992,992),('ordinary-bootstrap196',999,999)]:
 value=[1,2,uid,gid,stat.S_IFDIR|0o700,2,40,3,4]
 check(contract.role_metadata(name,value,uid,gid,[],True,True),True)
 for i,new in [(2,uid+1),(3,gid+1),(4,stat.S_IFDIR|0o755),(4,stat.S_IFLNK|0o700)]:
  bad=list(value);bad[i]=new;check(contract.role_metadata(name,bad,uid,gid,[],True,True),False)
 for bad in [None,[],value[:-1]]:check(contract.role_metadata(name,bad,uid,gid,[],True,True),False)
 for attrs in [['system.posix_acl_access'],['system.posix_acl_default'],None]:
  check(contract.role_metadata(name,value,uid,gid,attrs,True,True),False)
 check(contract.role_metadata(name,value,uid,gid,[],False,True),False)
 check(contract.role_metadata(name,value,uid,gid,[],True,False),False)
check(contract.role_metadata('ordinary-api',[1,2,999,999,stat.S_IFDIR|0o700,2,40,3,4],999,999,[],True,True),False)
literal=[1,2,0,0,stat.S_IFDIR|0o700,2,40,3,4]
for name in [None,[],{},'foreign']:
 check(contract.role_metadata(name,literal,0,0,[],True,True),False)
for index in range(9):
 for bad in [None,False,'unknown',-1]:
  value=list(literal);value[index]=bad;check(contract.role_metadata('root-api193',value,0,0,[],True,True),False)
for attrs in [[None],[[]],{None}]:check(contract.role_metadata('root-api193',literal,0,0,attrs,True,True),False)
root=pathlib.Path(__file__).resolve().parents[4]
ss=(root/'documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md').read_text()
for name in ['root-api193','root-web193','ordinary-api193','ordinary-web193','ordinary-inspector196','ordinary-bootstrap196']:
 check('`'+name+'`' in ss,True)
print('PG506_NAMESPACE_ORACLE independentAssertions='+str(n)+' approvedRoles6=true legacyRetained9=true liveVMActions0=true productionPT0=true')
