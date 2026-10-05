"""BUG724: independent vendor stop literal and negative vectors; no live process operations."""
import copy,json
import pg466_handoff as h
count=0
def check(b):
    global count
    count+=1
    if not b:raise AssertionError('broker vector '+str(count))
before={'MainPID':'1227864','InvocationID':'c784737af61e48778d0c8fa2c4f68037','ExecMainStartTimestampMonotonic':'100'}
after={'InvocationID':before['InvocationID'],'ExecMainStartTimestampMonotonic':'100','ExecMainExitTimestampMonotonic':'200','Result':'success','ExecMainCode':'1','ExecMainStatus':'143'}
row={'__CURSOR':'literal-1','__MONOTONIC_TIMESTAMP':'200','__REALTIME_TIMESTAMP':'1791160000000000','_BOOT_ID':'e07aa7061acd4e65b309d7f330f79d54','_SYSTEMD_UNIT':'artemis.service','_SYSTEMD_INVOCATION_ID':before['InvocationID'],'PRIORITY':'6','MESSAGE':'AMQ221002: Apache Artemis Message Broker version 2.56.0 [public-fixture] stopped, uptime 1 hour'}
def raw(r):return (json.dumps(r)+'\n').encode()
check(h.broker_witness(before,after,raw(row))['vendorStopData'])
for key in row:
    for kind in ('missing','null'):
        bad=copy.deepcopy(row)
        if kind=='missing':del bad[key]
        else:bad[key]=None
        try:h.broker_witness(before,after,raw(bad));raise AssertionError('invalid accepted')
        except ValueError:check(True)
for key,value in [('_SYSTEMD_UNIT','foreign.service'),('_BOOT_ID','a'*32),('_SYSTEMD_INVOCATION_ID','a'*32),('PRIORITY','3'),('__MONOTONIC_TIMESTAMP','99'),('__MONOTONIC_TIMESTAMP','201'),('MESSAGE','no stopped event'),('MESSAGE',row['MESSAGE']+' ERROR')]:
    bad=dict(row);bad[key]=value
    try:h.broker_witness(before,after,raw(bad));raise AssertionError('foreign accepted')
    except ValueError:check(True)
for bad in (raw(row)*2,raw(row)[:-1],b'{"MESSAGE":"x","MESSAGE":"y"}\n'):
    try:h.broker_witness(before,after,bad);raise AssertionError('duplicate accepted')
    except ValueError:check(True)
for key,value in [('InvocationID','a'*32),('Result','timeout'),('ExecMainCode','2'),('ExecMainStatus','137'),('ExecMainStartTimestampMonotonic','99')]:
    bad=dict(after);bad[key]=value
    try:h.broker_witness(before,bad,raw(row));raise AssertionError('manager accepted')
    except ValueError:check(True)
print('PG466_BROKER_ORACLE_PASS independentAssertions='+str(count)+' productionPT0=true mutation0=true')
