"""Real shared Current Chromium A01 on actual currenta9 captured ordinary owners."""
import inspect
import pg2720_operation_current_a01 as prior
from pg2862_network_newcurrent_observer import SOURCE,BOM
from pg1446_current_cold_stage import W


def code():
    live=prior.previous.json.loads((W/'pg2874-network-newcurrent-live-binding-v1/manifest.safe.json').read_bytes())
    if live.get('actualExit')!=0 or live.get('productionSource')!=SOURCE:raise ValueError('actual newa9 Root qualification required')
    raw=prior.code()
    old=prior.previous.json.loads((W/'pg2686-operation-current-live-binding-v1/manifest.safe.json').read_bytes())
    for a,b in [('PG2720','PG2884'),('pg2720','pg2884'),('pg2682','pg2862'),(prior.SOURCE,SOURCE),
        ('PG2654','PG2802'),('552c5e25591483ee2c9aa95c6b8170f37e3390b14bd08ed88bfc0c4870002a37',BOM),
        ('b2d6f605-61cf-425f-8fbd-12d606f6ee66','79a3260a-e16d-42bf-942a-b914ed144c28'),
        ('pg2684-operation-current-noargs-once-v2','pg2872-network-newcurrent-noargs-once-v2'),
        ('pg2680-operation-publication-post-v1','pg2860-network-cold-publication-independent-post-v1'),
        ("issued['MainPID']=='"+str(old['rootPid'])+"'","issued['MainPID']=='"+str(live['rootPid'])+"'"),
        ("m['InvocationID']=='"+old['binding']['invocation']+"'","m['InvocationID']=='"+live['binding']['invocation']+"'")]:
        if a not in raw:raise ValueError('all actual A01 producer/consumer roles required')
        raw=raw.replace(a,b)
    owner="""def require_socks_owner():
 import pg1191_chr_socks_owner as owner
 expected=json.loads((W/'pg2882-network-chr-socks-v1/running.safe.json').read_bytes())
 owner.EXPECTED={'pid':expected['pid'],'ticks':expected['ticks'],'argvSha256':expected['argvSha256'],
  'executable':'/usr/bin/ssh','ppid':expected['parentPid'],'uids':(1000,1000,1000,1000),
  'gids':(1000,1000,1000,1000),'listenerAddresses':('0100007F:D781',)}
 return owner.require_owner()
"""
    if raw.count('def main():')!=1:raise ValueError('one actual Browser scope required')
    raw=raw.replace('def main():',owner+'\ndef main():')
    raw=raw.replace('    before=json.loads(subprocess.check_output(ssh,input=GUARD.encode(),timeout=20))',
        '    socks=require_socks_owner()\n    before=json.loads(subprocess.check_output(ssh,input=GUARD.encode(),timeout=20))')
    raw=raw.replace('    after=json.loads(subprocess.check_output(ssh,input=GUARD.encode(),timeout=20))',
        '    assert require_socks_owner()==socks\n    after=json.loads(subprocess.check_output(ssh,input=GUARD.encode(),timeout=20))')
    from pyflakes.api import check
    if check(raw,'<whole actual newa9 A01>'):raise ValueError('complete shared Current A01 namespace required')
    compile(raw,'<same Root ordinary newa9 A01>','exec');return raw


def main():
    raw=code();ns={'__file__':__file__,'__name__':'newa9_a01'}
    exec(compile(raw,'<actual shared Current A01>','exec'),ns);ns['main']()


if __name__=='__main__':main()
