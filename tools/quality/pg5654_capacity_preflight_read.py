"""Fresh same-QEMU72GiB/source0ea geometry and host capacity; read only."""
import inspect
import hashlib
import json
import os
import pg4564_capacity_preflight_read as previous
from pg4996_resume_connection import authenticate_host
from pg5632_new_current_readonly import SOURCE,BOM

SLOT='pg5654-capacity-preflight-v2'


def qualify_layers(layers):
    expected=[('/home/mini/schubert-nk-pgpt/vm/pg2810-network-resume-cold-v1/active.qcow2',77309411328),
      ('/home/mini/schubert-nk-pgpt/vm/pg2200-outage-cold-v1/active.qcow2',51539607552),
      ('/home/mini/schubert-nk-pgpt/vm/pg1435-cold-v1/active.qcow2',51539607552),
      ('/home/mini/schubert-nk-pgpt/vm/pg1431/guest.qcow2',42949672960)]
    if type(layers)is not list or len(layers)!=4 or any(type(row)is not dict for row in layers):raise ValueError('exact active plus three backings')
    if [(row.get('filename'),row.get('virtualSize'))for row in layers]!=expected:raise ValueError('exact ordered paths and sizes')


HOST=previous.HOST.replace('60129542144','77309411328').replace('PG4564-read','PG5654-read').replace('PG4566-capacity-preflight-v1','PG5654-capacity-preflight-v2')
HOST=HOST.replace('assert len(layers)==3',inspect.getsource(qualify_layers)+"\nqualify_layers(layers)\n"+"""for layer in layers[1:]:
 matches=[fd for fd in(p/'fd').iterdir()if str(fd.readlink())==layer['filename']]
 assert len(matches)==1
 flags=next(line.split()[1]for line in(p/'fdinfo'/matches[0].name).read_text().splitlines()if line.startswith('flags:'))
 assert int(flags,8)&os.O_ACCMODE==os.O_RDONLY
""")
GUEST=(previous.GUEST.replace('93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de',BOM)
  .replace('964e96e45bb588e7e75798b5adf425cbd9985427',SOURCE).replace('58939391488','76119260672')
  .replace('pg4566-capacity-preflight-v1',SLOT))


def main():
    ns={**vars(previous),'HOST':HOST,'GUEST':GUEST,'authenticate_host':authenticate_host}
    raw=inspect.getsource(previous.main).replace('pg4566-capacity-preflight-v1',SLOT).replace('value=json.loads(output.strip())','value=decode_host_frame(output)')
    ns['decode_host_frame']=decode_host_frame
    exec(compile(raw,'<fresh current0ea QMP/geometry read>','exec'),ns)
    return ns['main']()


def decode_host_frame(output):
    lines=[line.strip()for line in output.splitlines()if line.strip()]
    if lines and lines[0]=='[sudo: ] Password:':lines=lines[1:]
    if len(lines)!=1 or not lines[0].startswith('{'):raise ValueError('one complete JSON frame after fixed optional sudo prompt')
    value=json.loads(lines[0])
    if type(value)is not dict or type(value.get('actualExit'))is not int or value['actualExit']!=0:raise ValueError('original actual host success required')
    return value


def recover_v2():
    authenticate_host();out=previous.W/SLOT
    if any((out/n).exists()for n in('host.safe.json','guest-observer.private.log','guest.safe.json','manifest.safe.json')):raise ValueError('original v2 recovery already advanced; inspect, do not replay')
    raw=(out/'host-observer.private.log').read_bytes()
    if hashlib.sha256(raw).hexdigest()!='87a6bcef7d2a38fdcca801d293947a44c11a44bf81cbb0c9cedcc982b178f8e9':raise ValueError('exact original host result')
    if (out/'host-payload.private.py').read_bytes()!=HOST.encode()or(out/'guest-payload.private.py').read_bytes()!=GUEST.encode():raise ValueError('original fixed payloads')
    value=decode_host_frame(raw.decode());qualify_layers(value['layers'])
    if value['resizeCommandsIssued']!=0 or value['bootChanged']is not False or value['jobs']!=[]or value['status']['status']!='running':raise ValueError('original read only QMP result')
    def save(name,value):
        with(out/name).open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    save('host.safe.json',value)
    r=previous.subprocess.run(previous.SSH+['sudo','-n','python3','-B','-'],input=GUEST.encode(),capture_output=True,timeout=100)
    with(out/'guest-observer.private.log').open('xb')as f:f.write(r.stdout+r.stderr);f.flush();os.fsync(f.fileno())
    if r.returncode!=0:raise ValueError('guest fresh geometry failed; preserve, no replay')
    guest=json.loads(r.stdout);save('guest.safe.json',guest)
    summary={'actualExit':0,'qemuVersion':value['greeting']['QMP']['version'],'hostAvailableBytes':value['hostAvailableBytes'],
      'oldVirtualSize':value['disk']['inserted']['image']['virtual-size'],'blockNode':value['disk']['inserted']['node-name'],'layers':len(value['layers']),
      'guestAvailableBytes':guest['availableBytes'],'minimumMet':guest['minimumMet'],'guestTools':guest['tools'],'operationsIssued':0,'source':guest['source'],
      'hostProofSha256':hashlib.sha256((out/'host.safe.json').read_bytes()).hexdigest(),'guestProofSha256':hashlib.sha256((out/'guest.safe.json').read_bytes()).hexdigest(),
      'hostReadRecoveredNotReplayed':True,'originalHostLogSha256':hashlib.sha256(raw).hexdigest()}
    save('manifest.safe.json',summary);print(json.dumps(summary));return 0


if __name__=='__main__':
    import sys
    if sys.argv[1:]not in([],['recover-v2']):raise SystemExit('noargs|recover-v2 only')
    raise SystemExit(recover_v2()if sys.argv[1:]else main())
