"""Independent same-source full11 and exact geometry before/after approved8GiB grow."""
import json
from pyflakes.api import check
import pg5632_new_current_readonly as current

BEFORE='pg5656-capacity-current-before-v1'
AFTER='pg5656-capacity-current-after-v1'
GROW='pg5658-capacity-online-grow-v1'


def geometry(after=False):
    raw="""geometry=json.loads(subprocess.check_output(['/usr/sbin/sfdisk','--json','/dev/vda'],timeout=10))['partitiontable']
disk_bytes=int(subprocess.check_output(['/usr/sbin/blockdev','--getsize64','/dev/vda'],timeout=10))
require(subprocess.check_output(['/usr/sbin/blkid','-s','UUID','-o','value','/dev/vda1'],timeout=10).strip()==b'92978eec-7925-481e-8629-5b963d59ced1')
require(geometry['label']=='gpt'and geometry['id']=='D1D80BB0-6CC8-4F75-96D7-429EFFC6A7E7'and geometry['sectorsize']==512)
require(len(geometry['partitions'])==4 and {p['node']for p in geometry['partitions']}=={'/dev/vda1','/dev/vda13','/dev/vda14','/dev/vda15'})
rootpart=next(p for p in geometry['partitions']if p['node']=='/dev/vda1')
require(rootpart['start']==2324480 and rootpart['uuid']=='F8A5DEDF-C7D3-42EA-96AA-30C2DB90705C')
"""
    if not after:
        return raw+"require(disk_bytes==77309411328 and rootpart['size']==148670431 and 0<free<12884901888)\n"
    return raw+"""before_geometry=json.loads((base/'pg5656-capacity-current-before-v1/partition-observed.private.json').read_bytes())
require(disk_bytes==85899345920 and free>=12884901888)
require(set(geometry)==set(before_geometry)and all(geometry[k]==before_geometry[k]for k in before_geometry if k not in {'partitions','lastlba'})and geometry['lastlba']==before_geometry['lastlba']+16777216)
oldroot=next(p for p in before_geometry['partitions']if p['node']=='/dev/vda1')
require(set(rootpart)==set(oldroot)and all(rootpart[k]==oldroot[k]for k in oldroot if k!='size')and rootpart['size']==oldroot['size']+16777216)
require([p for p in geometry['partitions']if p['node']!='/dev/vda1']==[p for p in before_geometry['partitions']if p['node']!='/dev/vda1'])
require(geometry==json.loads((base/'pg5658-capacity-online-grow-v1/partition-after.private.json').read_bytes()))
"""


def payload(after=False):
    raw=current.payload();slot=AFTER if after else BEFORE
    marker='free=os.statvfs(base).f_bavail*os.statvfs(base).f_frsize;require(free>=12884901888)'
    if raw.count(marker)!=1:raise ValueError('one original capacity gate')
    extra='free=os.statvfs(base).f_bavail*os.statvfs(base).f_frsize\n'+geometry(after)
    extra+="capacity_out=base/"+repr(slot)+";capacity_out.mkdir(mode=0o700)\n"
    extra+="with(capacity_out/'partition-observed.private.json').open('x')as saved:\n json.dump(geometry,saved,sort_keys=True);saved.flush();os.fsync(saved.fileno())\n"
    raw=raw.replace(' '+marker,'\n'.join(' '+line for line in extra.splitlines()),1)
    if check(raw,'<full11 and geometry before or after>'):raise ValueError('complete static0')
    compile(raw,'<independent full11/geometry>','exec');return raw


def main(after=False):
    if after:
        receipt=json.loads((current.post.role.W/(GROW+'/manifest.safe.json')).read_bytes())
        if type(receipt['actualExit'])is not int or receipt['actualExit']!=0:raise ValueError('actual original grow0 before independent after')
    current.authenticate_host();transport=current.previous.transport
    import types
    return types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':current.SOURCE})(AFTER if after else BEFORE,payload(after),180)


if __name__=='__main__':
    import sys
    if sys.argv[1:]not in(['before'],['after']):raise SystemExit('before|after required')
    raise SystemExit(main(sys.argv[1:]==['after']))
