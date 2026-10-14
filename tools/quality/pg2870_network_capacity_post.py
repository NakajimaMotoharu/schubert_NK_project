"""Independent entire current/raw data + same boot56 geometry and capacity after grow."""
import inspect
from pyflakes.api import check
import pg2860_network_cold_publication_post as prior
import pg1453_current_cold_post as runner
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate
from pg2814_network_newboot_readonly import one

SLOT='pg2870-network-capacity-independent-post-v1'


def payload():
    raw=prior.payload().replace(prior.SLOT,SLOT).replace('PG2860-network-cold-publication-independent-post-v1','PG2870-network-capacity-independent-post-v1')
    extra=""" before_geometry=json.loads((BASE/'pg2868-network-online-grow-v1/partition-before.private.json').read_bytes())
 geometry=json.loads(command(['/usr/sbin/sfdisk','--json','/dev/vda'],1048576))['partitiontable']
 require(command(['/usr/sbin/blockdev','--getsize64','/dev/vda'],4096).strip()==b'60129542144')
 require(set(geometry)==set(before_geometry)and all(geometry[k]==before_geometry[k]for k in before_geometry if k not in {'partitions','lastlba'})and geometry['lastlba']==before_geometry['lastlba']+16777216)
 old_root=next(v for v in before_geometry['partitions']if v['node']=='/dev/vda1')
 new_root=next(v for v in geometry['partitions']if v['node']=='/dev/vda1')
 require(set(new_root)==set(old_root)and all(new_root[k]==old_root[k]for k in old_root if k!='size')and new_root['size']==old_root['size']+16777216)
 require([v for v in geometry['partitions']if v['node']!='/dev/vda1']==[v for v in before_geometry['partitions']if v['node']!='/dev/vda1'])
 fs=os.statvfs('/var/lib/pgpt-s1-preservation');free=fs.f_bavail*fs.f_frsize;require(free>=12884901888)
 require(geometry==json.loads((BASE/'pg2868-network-online-grow-v1/partition-after.private.json').read_bytes()))
 failed=BASE/'pg2864-network-newcurrent-noargs-once-v1';require(not os.path.lexists(failed/'external-start-guard.private.json')and not os.path.lexists(failed/'external-start-issued.private.json'))
"""
    raw=one(raw,'finally:\n errors=[]',extra+'finally:\n errors=[]')
    raw=one(raw,"'businessWrites':0,","'businessWrites':0,'sameBootOnlineCapacity':True,'rootStartUuidTypePreserved':True,'otherPartitionsUnchanged':True,'guestFreeBytes':free,'diskBytes':60129542144,'oldOrdinaryGuardStartAbsent':True,")
    if check(raw,'<full independent capacity and current after>'):raise ValueError('complete same source geometry namespace required')
    compile(raw,'<actual independent56 capacity/current post>','exec');return raw


def main():
    actual=runner.json.loads((W/'pg2868-network-online-capacity-grow-v1/manifest.safe.json').read_bytes())
    if actual.get('actualExit')!=0:raise ValueError('actual normal one online grow required')
    raw=inspect.getsource(runner.main).replace('pg1452-current-cold-owned-prepare-v1','pg2858-network-cold-publication-owned-activate-v1').replace('pg1453-current-cold-independent-post-v1',SLOT)
    ns={**runner.__dict__,'payload':payload,'W':W}
    exec(compile(raw,'<whole capacity geometry separate post dispatcher>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
