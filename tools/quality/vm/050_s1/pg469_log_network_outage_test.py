"""Literal persisted ERROR/SENT and exact-once DB oracles; never production-derived."""
import copy
from pg469_log_network_outage import blocked_rows,recovered_rows
keys=['00000000-0000-0000-0000-'+str(i).zfill(12) for i in range(1,6)]
blocked={'outbox':[{'event':k,'status':'ERROR','attempts':1} for k in keys],'db':[]}
recovered={'outbox':[{'event':k,'status':'SENT','attempts':1} for k in keys],
 'db':[{'event':k,'category':'REQUEST','action':'HTTP_REQUEST_COMPLETED','service':'WEB'} for k in keys]}
checks=0
def check(value):
 global checks
 assert value
 checks+=1
check(blocked_rows(blocked,keys));check(recovered_rows(recovered,keys))
for fn,fixture in [(blocked_rows,blocked),(recovered_rows,recovered)]:
 for v in [None,[],{}, {'outbox':None,'db':[]}, {'outbox':[],'db':None}]:check(not fn(v,keys))
 for field in ['event','status','attempts']:
  for value in [None,False,True,'foreign',-1,0,1.0,[],{}]:
   v=copy.deepcopy(fixture);v['outbox'][0][field]=value;check(not fn(v,keys))
 for change in ['missing','duplicate','foreign','extra']:
  v=copy.deepcopy(fixture)
  if change=='missing':v['outbox'].pop()
  elif change=='duplicate':v['outbox'].append(copy.deepcopy(v['outbox'][0]))
  elif change=='foreign':v['outbox'][0]['event']='00000000-0000-0000-0000-000000000099'
  else:v['outbox'][0]['secret']='forbidden'
  check(not fn(v,keys))
v=copy.deepcopy(blocked);v['db']=copy.deepcopy(recovered['db']);check(not blocked_rows(v,keys))
for field in ['event','category','action','service']:
 for value in [None,1,'foreign','',[],{}]:
  v=copy.deepcopy(recovered);v['db'][0][field]=value;check(not recovered_rows(v,keys))
for change in ['missing','duplicate','extra']:
 v=copy.deepcopy(recovered)
 if change=='missing':v['db'].pop()
 elif change=='duplicate':v['db'].append(copy.deepcopy(v['db'][0]))
 else:v['db'][0]['secret']='forbidden'
 check(not recovered_rows(v,keys))
print('PG469_LOG_OUTAGE_ORACLE independentAssertions='+str(checks)+' nativeMutation0=true')
