"""Normal owned fixture poweroff only; primary VM and every old proof retained.

SS343/451/PT-OPS-LFACT-POWER001..003. Request once; verify never reissues.
UNKNOWN is retained, not promoted from network loss. No destructive signal.
"""
import argparse
import json
import os
import subprocess
from pyflakes.api import check
from lan_server import run
import pg3216_legacy_negative_dispatch as transport
from pg1446_current_cold_stage import W

OUT = W / 'pg3240-negative-fixture-poweroff-v1'
GUEST = r'''
import datetime,hashlib,json,os,sys
from pathlib import Path
stage=Path('/home/ubuntu/pg3236-legacy-negative-v1')
for name,digest in HASHES.items():assert hashlib.sha256((stage/name).read_bytes()).hexdigest()==digest
sys.path.insert(0,str(stage))
import pg3216_legacy_negative_observer as o
import pg3218_legacy_negative_retained as c
o.guard();c.runtime_fixed();root=o.BASE/'observer-cohort-v5'
post=json.loads((root/'independent-post.safe.json').read_text());whole=json.loads((root/'manifest.safe.json').read_text())
o.require(post['actualExit']==whole['actualExit']==0 and whole['source']==o.SOURCE and whole['boot']==o.BOOT and o.sha(o.BASE/'cohort-native-v5.exec')==post['nativeSha256'])
before=json.loads((root/'before.private.json').read_text());o.require(o.tree()==before['tree']and o.database()==before['database']and o.stable_bad()==before['bad'])
for name in post['unitStates']:
 text=o.command(['systemctl','show',name,'-p','ActiveState','-p','SubState','-p','MainPID','-p','ControlPID','-p','Job']).stdout
 o.require(dict(line.split('=',1)for line in text.splitlines())=={'ActiveState':'inactive','SubState':'dead','MainPID':'0','ControlPID':'0','Job':''})
 group=Path('/sys/fs/cgroup/system.slice')/name;o.require(not group.exists()or not(group/'cgroup.procs').read_text().strip())
o.require(not Path('/proc',str(whole['pid'])).exists())
versions={'os':Path('/etc/os-release').read_text(),'jdk':o.command(['/usr/bin/java','--version']).stdout,'strace':o.command(['/usr/bin/strace','--version']).stdout.splitlines()[0],'systemd':o.command(['systemctl','--version']).stdout.splitlines()[0]}
reservation={'issuedOnce':True,'purpose':'ISOLATED_NEGATIVE_FIXTURE_NORMAL_POWEROFF','boot':o.BOOT,'source':o.SOURCE,'normalBusinessStarts':0,'postSha256':o.sha(root/'independent-post.safe.json'),'timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'toolchain':versions}
with(root/'poweroff-reservation.safe.json').open('x')as f:json.dump(reservation,f,sort_keys=True);f.flush();os.fsync(f.fileno())
r=o.command(['systemctl','poweroff','--no-block'],timeout=10)
print(json.dumps({'actualExit':r.returncode,'normalPoweroffRequested':True,'boot':o.BOOT,'newBusinessStarts':0,'toolchain':versions}),flush=True)
'''

BEFORE = r'''
import sys,json
from pathlib import Path
sys.path.insert(0,'/home/mini/schubert-nk-pgpt/tools/pg3210-negative-fixed-v1')
import pg3210_legacy_negative_vm as v
v.primary(445092)
out=Path('/home/mini/schubert-nk-pgpt/vm/pg3210-legacy-negative-v1');p=out/'console.private.log';s=p.stat()
print(json.dumps({'actualExit':0,'serialBefore':[s.st_dev,s.st_ino,s.st_size],'hostBoot':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'fixtureOwner':FIXTURE,'primaryUntouched':True}))
'''

AFTER = r'''
import hashlib,json,stat,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/mini/schubert-nk-pgpt/tools/pg3210-negative-fixed-v1')
import pg3210_legacy_negative_vm as v
until=time.monotonic()+40
while Path('/proc/445092').exists()and time.monotonic()<until:time.sleep(.2)
v.require(not Path('/proc/445092').exists());v.primary()
v.require(not subprocess.check_output(['ss','-H','-lnt','( sport = :22224 )']))
out=Path('/home/mini/schubert-nk-pgpt/vm/pg3210-legacy-negative-v1');serial=out/'console.private.log';s=serial.stat()
v.require([s.st_dev,s.st_ino]==PRIOR['serialBefore'][:2]and s.st_size>PRIOR['serialBefore'][2])
with serial.open('rb')as f:f.seek(PRIOR['serialBefore'][2]);tail=f.read()
v.require(b'Power down'in tail or b'Powering off'in tail)
info=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(out/'active.qcow2')]))
v.require(len(info)==4 and info[0]['filename']==str(out/'active.qcow2')and info[0]['format']=='qcow2')
v.original.validate_chain(info[1:]);v.chain(v.reference(),False)
for row in info:
 data=row.get('format-specific',{}).get('data',{});v.require(data.get('corrupt',False)is False and row.get('dirty-flag',False)is False)
disk=out/'active.qcow2';target=disk.stat();openers=[]
for process in Path('/proc').iterdir():
 if not process.name.isdigit():continue
 try:
  for fd in(process/'fd').iterdir():
   try:a=fd.stat()
   except FileNotFoundError:continue
   if(a.st_dev,a.st_ino)==(target.st_dev,target.st_ino):openers.append(int(process.name))
 except FileNotFoundError:continue
v.require(openers==[] and stat.S_ISREG(target.st_mode)and target.st_nlink==1)
print(json.dumps({'actualExit':0,'fixtureQemuGone':True,'fixtureServerPortGone':True,'normalGuestPowerDownInNewSerial':True,'serialDeltaSha256':hashlib.sha256(tail).hexdigest(),'fixtureDiskNoOpeners':True,'fourLayerClean':True,'primaryUntouched':True,'oldBackingIdentitiesUnchanged':True,'source':'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25','businessStarts':0,'formalAccepted':False}))
'''


def save(name, value):
    with (OUT / name).open('x') as file:
        json.dump(value, file, sort_keys=True); file.flush(); os.fsync(file.fileno())


def server(raw, name, timeout=60):
    if check(raw, '<complete fixed fixture poweroff boundary>'): raise ValueError('whole namespace required')
    code, output = run("python3 -B - <<'OWNED'\n" + raw + '\nOWNED', timeout=timeout, sudo=True)
    (OUT / name).write_text(output)
    if code: raise ValueError('owned shutdown proof unavailable; never request again')
    return json.loads(next(line for line in output.splitlines() if line.startswith('{')))


def request():
    transport.owners()
    native = json.loads((W / 'pg3234-legacy-negative-native-v1/manifest.safe.json').read_text())
    if native['actualExit'] != 0 or native['result']['distinctSessions'] != 28: raise ValueError('qualified successful native28 required')
    OUT.mkdir(mode=0o700)
    before = server('FIXTURE=' + repr(transport.FIXTURE) + '\n' + BEFORE, 'before.private.log')
    save('request-reservation.safe.json', {'issuedOnce': True, 'before': before, 'fixtureOwner': transport.FIXTURE, 'nativeManifestSha256': native['manifestSha256']})
    stage = json.loads((W / 'pg3236-legacy-negative-v1/stage.safe.json').read_text())
    raw = 'HASHES=' + repr(stage['hashes']) + '\n' + GUEST
    if check(raw, '<whole fixture guest normal poweroff>'): raise ValueError('complete guest namespace required')
    with (OUT / 'request.private.log').open('xb') as log, (OUT / 'request.private.err').open('xb') as err:
        result = subprocess.run(transport.ssh() + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), stdout=log, stderr=err, timeout=30)
    save('request.safe.json', {'actualExit': result.returncode, 'networkLossNotSuccess': True})
    if result.returncode != 0: raise ValueError('shutdown response uncertain; verify only, never repeat')
    received = json.loads((OUT / 'request.private.log').read_text())
    if received['actualExit'] != 0 or received['boot'] != transport.BOOT: raise ValueError('same-boot normal poweroff ACK required')
    print('PG3240_REQUEST actual0=true normalPoweroffAck=true primaryKept=true', flush=True)


def verify():
    prior = json.loads((OUT / 'request-reservation.safe.json').read_text())
    value = server('PRIOR=' + repr(prior['before']) + '\n' + AFTER, 'after.private.log')
    ack = json.loads((OUT / 'request.safe.json').read_text())
    value['requestActualExit'] = ack['actualExit']
    save('server-post.safe.json', value)
    print(json.dumps(value), flush=True)


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['request', 'verify']); phase = parser.parse_args().phase
    (request if phase == 'request' else verify)()


if __name__ == '__main__':
    main()
