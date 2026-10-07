"""BUG818/YKT587: exact PG502 cold-after lock reference, NOT PG504 runtime schema."""
import stat
def cold_lock_reference(value):
 if not isinstance(value,dict) or set(value)!={'units','rows','trees','owner','prepared'} or value['prepared'] is not True:return False
 owner=value['owner']
 if not isinstance(owner,list) or len(owner)!=3 or type(owner[0]) is not int or owner[0]<2 or type(owner[1]) is not int or owner[1]<1:return False
 locks=owner[2]
 if not isinstance(locks,dict) or set(locks)!={'maintenance.lock','startup-admission.lock'}:return False
 for v in locks.values():
  if not isinstance(v,list) or len(v)!=9 or any(type(x) is not int or x<0 for x in v):return False
  if v[1]<1 or v[2:7]!=[0,0,stat.S_IFREG|0o600,1,0]:return False
 return isinstance(value['units'],dict) and len(value['units'])==10 and isinstance(value['rows'],dict) and len(value['rows'])==24 and isinstance(value['trees'],dict)
