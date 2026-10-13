"""Unchanged current/DB/originals and independent disk geometry/space after online grow."""
import inspect
import pg2006_existing_runtime_independent_post as prior
from pg1877_warning_publication_sources import once

SLOT='pg2013-online-capacity-independent-post-v1'


def payload():
    raw=prior.payload().replace(prior.SLOT,SLOT)
    marker="save=base/'"+SLOT+"'"
    extra=r'''
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='3d69f5af-6bac-46b1-a540-7591c4a79a0d')
require(command(['/usr/sbin/blockdev','--getsize64','/dev/vda']).strip()==b'51539607552')
geometry=json.loads(command(['/usr/sbin/sfdisk','--json','/dev/vda']))['partitiontable']
saved=json.loads((base/'pg2012-online-grow-v1/partition-before.private.json').read_bytes())
require(set(geometry)==set(saved)and all(geometry[k]==saved[k]for k in saved if k not in {'partitions','lastlba'})and geometry['lastlba']==saved['lastlba']+16777216)
before_root=next(p for p in saved['partitions']if p['node']=='/dev/vda1');after_root=next(p for p in geometry['partitions']if p['node']=='/dev/vda1')
require(set(before_root)==set(after_root)and all(after_root[k]==before_root[k]for k in before_root if k!='size')and after_root['size']==before_root['size']+16777216)
require([p for p in geometry['partitions']if p['node']!='/dev/vda1']==[p for p in saved['partitions']if p['node']!='/dev/vda1'])
free=os.statvfs('/var/lib/pgpt-s1-preservation').f_bavail*os.statvfs('/var/lib/pgpt-s1-preservation').f_frsize;require(free>=12*1024**3)
require(pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists()is False)
'''
    raw=once(raw,marker,extra+'\n'+marker)
    raw=raw.replace("'existingFileNoRewrite':True","'existingFileNoRewrite':True,'sameBootAfterOnlineCapacityGrow':True,'rootPartitionStartUuidTypePreserved':True,'otherPartitionsUnchanged':True,'guestFreeBytes':free")
    from pyflakes.api import check
    if check(raw,'<actual independent capacity/current post>'):raise ValueError('all post globals required')
    compile(raw,'<same current whole post plus capacity>','exec');return raw


def main():
    actual=prior.prior.json.loads((prior.prior.W/'pg2012-online-capacity-grow-v1/manifest.safe.json').read_bytes())
    if actual['actualExit']!=0:raise ValueError('actual normal one capacity growth required')
    ns={**prior.prior.__dict__,'SLOT':SLOT,'payload':payload}
    raw=inspect.getsource(prior.prior.main).replace('pg1983-prepare-resume-v1.safe.json','pg2003-finish-runtime-v1.safe.json')
    exec(compile(raw,'<independent actual capacity fullpost entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
