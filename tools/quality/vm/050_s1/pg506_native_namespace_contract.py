"""BUG813/YKT582 SS343 SSC193/196 fixed catalog. Pure guards only, no VM authority."""
import stat

ROLES={'root-api193':'root','root-web193':'root','ordinary-api193':'schubert-api',
 'ordinary-web193':'schubert-web','ordinary-inspector196':'schubert-inbox-inspector',
 'ordinary-bootstrap196':'schubert-api'}
UNIT_ROLES={'schubert-nk-api.service':{'root-api193','ordinary-api193'},
 'schubert-nk-web.service':{'root-web193','ordinary-web193'},
 'schubert-nk-inbox-inspector.service':{'ordinary-inspector196'},
 'schubert-nk-bootstrap-admin.service':{'ordinary-bootstrap196'}}
LEGACY={'parent','backup','cleanup','expiry','inspector','root-api','root-web','ordinary-api','ordinary-web'}

def catalog(actual):
 return isinstance(actual,set) and actual==set(ROLES)|LEGACY
def effective_roles(actual):
 return (isinstance(actual,dict) and set(actual)==set(UNIT_ROLES)
  and all(isinstance(v,set) and v==UNIT_ROLES[k] for k,v in actual.items()))
def role_metadata(name,values,uid,gid,xattrs,tmpfs,empty):
 return (isinstance(name,str) and name in ROLES and isinstance(values,list) and len(values)==9
  and all(type(v) is int and v>=0 for v in values) and values[1]>0 and values[5]>=2
  and type(uid) is int and type(gid) is int and uid>=0 and gid>=0
  and values[2:5]==[uid,gid,stat.S_IFDIR|0o700]
  and isinstance(xattrs,(list,set)) and all(isinstance(v,str) for v in xattrs)
  and not {'system.posix_acl_access','system.posix_acl_default'}.intersection(xattrs)
  and tmpfs is True and empty is True and (ROLES[name]!='root' or uid==gid==0))
