"""Independent read-only private VM check. Print metadata/hashes only, never native IDs/bytes."""
import hashlib, json, os, pathlib, re, stat, subprocess

root = pathlib.Path('/run/schubert-nk/startup')
def sha(value): return hashlib.sha256(value).hexdigest()
def read(name):
    fd = os.open(root/name, os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        assert stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600
        assert before.st_uid == before.st_gid == 0 and before.st_nlink == 1 and before.st_size <= 65536
        content = b''
        while block := os.read(fd,65536): content += block
        assert before == os.fstat(fd) and len(content) == before.st_size
        # getfacl's access entries must have no named user/group/mask/default additions.
        acl = subprocess.check_output(['/usr/bin/getfacl','-cp',str(root/name)],text=True)
        assert [v for v in acl.splitlines() if v] == ['user::rw-','group::---','other::---']
        return content
    finally: os.close(fd)

current = read('epoch.current')
def fields(content, header, names):
    text = content.decode('ascii')
    lines = text.splitlines()
    assert text.endswith('\n') and lines[0] == header and len(lines) == len(names)+1
    assert [v.split('=',1)[0] for v in lines[1:]] == names
    return dict(v.split('=',1) for v in lines[1:])

binding = ['boot_id','epoch_id','run_id','cutoff_utc','activation_id']
epoch = fields(current,'NKEPOCH1',['state']+binding+['permit_sha256'])
assert epoch['state'] == 'ISSUED'
for key in ['boot_id','epoch_id','run_id','activation_id']:
    assert re.fullmatch(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}',epoch[key])
permit = read(epoch['epoch_id']+'.permit')
values = fields(permit,'NKPERMIT1',binding+['broker_invocation_id','release_sha256',
    'api_config_sha256','web_config_sha256','roots_sha256','prestart_steps_sha256'])
assert all(epoch[k] == values[k] for k in binding)
assert sha(permit) == epoch['permit_sha256']
assert epoch['boot_id'] == pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
assert re.fullmatch(r'[0-9a-f]{32}',values['broker_invocation_id'])
inv = subprocess.check_output(['/usr/bin/systemctl','show','artemis.service','-p','InvocationID','--value'],text=True).strip()
assert values['broker_invocation_id'] == inv
for key in ['release_sha256','api_config_sha256','web_config_sha256','roots_sha256','prestart_steps_sha256']:
    assert re.fullmatch(r'[0-9a-f]{64}',values[key])
assert values['release_sha256'] == sha(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes())
assert not (root/'permit-start.intent').exists()
assert not any(p.name.endswith('.part') or p.name.endswith('.intent') for p in root.iterdir())

# SS343 NKROOTS1 byte offset/order, independently assembled from host kernel metadata.
paths = [('ASSET','/srv/schubert-nk/data/assets'),('TRANSFER','/srv/schubert-nk/data/transfer'),
    ('BACKUP','/srv/schubert-nk/backup'),('LOG','/var/log/schubert-nk'),
    ('ARTEMIS','/var/lib/schubert-nk/artemis'),('STAGING','/srv/schubert-nk/staging')]
frame = 'NKROOTS1\n'+''.join(k+'='+epoch[k]+'\n' for k in binding)
for role,path in paths:
    metadata = os.stat(path,follow_symlinks=False)
    assert stat.S_ISDIR(metadata.st_mode)
    fs = subprocess.check_output(['/usr/bin/findmnt','-n','-o','FSTYPE','-T',path],text=True).strip()
    acl = subprocess.check_output(['/usr/bin/getfacl','-cp',path],text=True)
    assert all(v.startswith(('user::','group::','other::')) for v in acl.splitlines() if v)
    frame += '|'.join(map(str,[role,path,metadata.st_dev,metadata.st_ino,metadata.st_uid,
        metadata.st_gid,format(stat.S_IMODE(metadata.st_mode),'04o'),fs,'0','empty']))+'\n'
assert sha(frame.encode('ascii')) == values['roots_sha256']
assert current == read('epoch.current') and permit == read(epoch['epoch_id']+'.permit')
print(json.dumps({'currentState':'ISSUED','permitHashBinding':True,'bootBinding':True,
    'brokerInvocationBinding':True,'releaseManifestBinding':True,'independentSixRootBytesMatch':True,
    'currentSha256':sha(current),'permitSha256':sha(permit),'rootsFrameSha256':sha(frame.encode('ascii')),
    'intentEntries':0,'wholeStartupAccepted':False,'readyAccepted':False}))
