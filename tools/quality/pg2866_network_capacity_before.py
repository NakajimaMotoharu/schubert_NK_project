"""Fresh full newcurrent read-only admission failure proof, capacity/geometry before."""
import inspect
from pyflakes.api import check
import pg2860_network_cold_publication_post as prior
import pg1453_current_cold_post as runner
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate
from pg2814_network_newboot_readonly import one

SLOT='pg2866-network-capacity-before-v1'


def payload():
    raw=prior.payload().replace(prior.SLOT,SLOT).replace('PG2860-network-cold-publication-independent-post-v1','PG2866-network-capacity-before-v1')
    extra=""" failed=BASE/'pg2864-network-newcurrent-noargs-once-v1'
 require(not os.path.lexists(failed/'external-start-guard.private.json')and not os.path.lexists(failed/'external-start-issued.private.json'))
 geometry=json.loads(command(['/usr/sbin/sfdisk','--json','/dev/vda'],1048576))['partitiontable']
 disk_bytes=int(command(['/usr/sbin/blockdev','--getsize64','/dev/vda'],4096))
 fs=os.statvfs('/var/lib/pgpt-s1-preservation');free=fs.f_bavail*fs.f_frsize
 require(disk_bytes==51539607552 and free<12884901888 and free>10*1024**3)
 with(SAVE/'partition-before.private.json').open('xb')as f:f.write(json.dumps(geometry,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
"""
    raw=one(raw,'finally:\n errors=[]',extra+'finally:\n errors=[]')
    raw=one(raw,"'businessWrites':0,","'businessWrites':0,'oldOrdinaryGuardStartAbsent':True,'guestFreeBytes':free,'diskBytes':disk_bytes,'partitionBeforeSha256':hashlib.sha256(json.dumps(geometry,sort_keys=True).encode()).hexdigest(),")
    if check(raw,'<full capacity and no-start before>'):raise ValueError('complete capacity before namespace required')
    compile(raw,'<actual current capacity before>','exec');return raw


def main():
    raw=inspect.getsource(runner.main).replace('pg1452-current-cold-owned-prepare-v1','pg2858-network-cold-publication-owned-activate-v1').replace('pg1453-current-cold-independent-post-v1',SLOT)
    ns={**runner.__dict__,'payload':payload,'W':W}
    exec(compile(raw,'<full no-start capacity before dispatcher>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
