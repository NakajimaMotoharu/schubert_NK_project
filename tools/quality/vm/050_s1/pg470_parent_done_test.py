"""Literal PID1 completion oracle. No native execution or authority mutation."""
from pg470_live_peer_check import parent_done
row={'_BOOT_ID':'e07aa7061acd4e65b309d7f330f79d54','_PID':'1','_UID':'0','_COMM':'systemd','MESSAGE_ID':'39f53479d3a045ac8e11786248231fbf','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'aabcc2c3ef1444a7bb07b3183b220c14','JOB_ID':'162935','JOB_TYPE':'start','JOB_RESULT':'done','__REALTIME_TIMESTAMP':'1791219312310761','_SOURCE_REALTIME_TIMESTAMP':'1791219312310761'}
checks=0
def check(ok):
 global checks
 assert ok,'literal PID1 oracle'
 checks+=1
check(parent_done(row));check(not parent_done(None));check(not parent_done([]))
for key in row:
 for value in [None,'foreign',1,True]:check(not parent_done({**row,key:value}))
 wrong=dict(row);del wrong[key];check(not parent_done(wrong))
for key in ['__REALTIME_TIMESTAMP','_SOURCE_REALTIME_TIMESTAMP']:
 for value in ['1791218059999999','1791219861000001','01791219312310761','179121931231076','１７９１２１９３１２３１０７６１']:check(not parent_done({**row,key:value}))
 for value in ['1791218060000000','1791219861000000']:check(parent_done({**row,key:value}))
print('PG470_PARENT_DONE independentAssertions='+str(checks)+' productionPT0=true nativeMutation0=true')
