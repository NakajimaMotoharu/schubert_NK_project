"""Fresh full11/source proof with independent online-capacity geometry; no mutation."""
import inspect
from pyflakes.api import check
import pg4546_failed_current_publication_post as current
from pg2814_network_newboot_readonly import one

BEFORE='pg4570-capacity-current-before-v1'
AFTER='pg4574-capacity-current-after-v1'


def geometry(after=False):
    raw=""" geometry=json.loads(command(['/usr/sbin/sfdisk','--json','/dev/vda'],1048576))['partitiontable']
 disk_bytes=int(command(['/usr/sbin/blockdev','--getsize64','/dev/vda'],4096))
 require(command(['/usr/sbin/blkid','-s','UUID','-o','value','/dev/vda1'],4096).strip()==b'92978eec-7925-481e-8629-5b963d59ced1')
 require(geometry['label']=='gpt'and geometry['id']=='D1D80BB0-6CC8-4F75-96D7-429EFFC6A7E7'and geometry['sectorsize']==512)
 require(len(geometry['partitions'])==4 and {p['node']for p in geometry['partitions']}=={'/dev/vda1','/dev/vda13','/dev/vda14','/dev/vda15'})
 free=os.statvfs('/var/lib/pgpt-s1-preservation').f_bavail*os.statvfs('/var/lib/pgpt-s1-preservation').f_frsize
 save_private('partition-observed.private.json',geometry)
 save_private('capacity-observed.private.json',{'diskBytes':disk_bytes,'freeBytes':free})
"""
    if not after:
        raw+=""" require(disk_bytes==60129542144)
 rootpart=next(p for p in geometry['partitions']if p['node']=='/dev/vda1')
 require(rootpart['start']==2324480 and rootpart['size']==115115999 and rootpart['uuid']=='F8A5DEDF-C7D3-42EA-96AA-30C2DB90705C')
 require(0<free<12884901888)
"""
    else:
        raw+=""" before_geometry=json.loads((base/'pg4570-capacity-current-before-v1/partition-observed.private.json').read_bytes())
 require(disk_bytes==77309411328 and free>=12884901888)
 require(set(geometry)==set(before_geometry)and all(geometry[k]==before_geometry[k]for k in before_geometry if k not in {'partitions','lastlba'})and geometry['lastlba']==before_geometry['lastlba']+33554432)
 oldroot=next(p for p in before_geometry['partitions']if p['node']=='/dev/vda1');newroot=next(p for p in geometry['partitions']if p['node']=='/dev/vda1')
 require(set(newroot)==set(oldroot)and all(newroot[k]==oldroot[k]for k in oldroot if k!='size')and newroot['size']==oldroot['size']+33554432)
 require([p for p in geometry['partitions']if p['node']!='/dev/vda1']==[p for p in before_geometry['partitions']if p['node']!='/dev/vda1'])
 require(geometry==json.loads((base/'pg4572-capacity-online-grow-v1/partition-after.private.json').read_bytes()))
"""
    return raw


def payload(after=False):
    slot=AFTER if after else BEFORE
    raw=current.payload().replace(current.SLOT,slot)
    raw=one(raw,'finally:\n for unit in reversed(refs):',geometry(after)+'finally:\n for unit in reversed(refs):')
    raw=one(raw,"'dbWrites':0,'signalsOrStarts':0,","'dbWrites':0,'signalsOrStarts':0,'diskBytes':disk_bytes,'guestFreeBytes':free,'geometrySha256':hashlib.sha256(json.dumps(geometry,sort_keys=True).encode()).hexdigest(),")
    if check(raw,'<full current and exact capacity>'):raise ValueError('all emitted static0')
    return raw


def main(after=False):
    if after:
        receipt=current.json.loads((current.W/'pg4572-capacity-online-grow-v1/manifest.safe.json').read_bytes())
        if receipt['actualExit']!=0:raise ValueError('genuine once grow0 first')
    ns={**vars(current),'SLOT':AFTER if after else BEFORE,'payload':lambda:payload(after)}
    exec(compile(inspect.getsource(current.main),'<new full current capacity dispatcher>','exec'),ns)
    return ns['main']()


if __name__=='__main__':
    import sys
    if sys.argv[1:]not in (['before'],['after']):raise SystemExit('before|after required')
    raise SystemExit(main(sys.argv[1:]==['after']))
