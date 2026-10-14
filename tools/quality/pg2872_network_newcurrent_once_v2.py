"""Separate once scope after capacity fullpost; old v1 never reissued or normalized."""
import inspect
import pg2864_network_newcurrent_once as prior
from pg2814_network_newboot_readonly import one

SLOT='pg2872-network-newcurrent-noargs-once-v2'


def require_capacity(free):
    if type(free)is not int or free<12884901888:
        raise ValueError('12GiB capacity admission unavailable; no guard or start issued')


def payload(hashes):
    raw=prior.payload(hashes).replace(prior.SLOT,SLOT).replace('PG2864-network-newcurrent-noargs-once-v1','PG2872-network-newcurrent-noargs-once-v2')
    old="require(os.statvfs('/var/lib/pgpt-s1-preservation').f_bavail*os.statvfs('/var/lib/pgpt-s1-preservation').f_frsize>=12884901888)"
    raw=one(raw,old,"require_capacity(os.statvfs('/var/lib/pgpt-s1-preservation').f_bavail*os.statvfs('/var/lib/pgpt-s1-preservation').f_frsize)")
    raw=inspect.getsource(require_capacity)+'\n'+raw
    from pyflakes.api import check
    if check(raw,'<whole capacity-qualified fresh once v2>'):raise ValueError('complete v2 current once namespace required')
    compile(raw,'<new-only v2 once after capacity>','exec');return raw


def main():
    v=prior.json.loads((prior.W/'pg2870-network-capacity-independent-post-v1/manifest.safe.json').read_bytes())
    g=v.get('guest',{})
    if v.get('actualExit')!=0 or g.get('sameBootOnlineCapacity')is not True or g.get('oldOrdinaryGuardStartAbsent')is not True:
        raise ValueError('independent capacity/current/no-old-start proof required')
    require_capacity(g.get('guestFreeBytes'))
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(prior.main),'<new once currentv2 after full geometry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
