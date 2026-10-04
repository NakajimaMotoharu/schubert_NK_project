"""New-only isolated candidate/operator placement. No activation/start/migration/permit authority."""
import hashlib, pathlib, subprocess
work=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
private=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
ssh=['ssh','-i',str(private/'vm-access'),'-p','22222','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(private/'known_hosts'),'ubuntu@127.0.0.1']
scp=['scp','-i',str(private/'vm-access'),'-P','22222','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(private/'known_hosts')]
names=['Pg387TrustedDeployment','Pg387TrustedDeployment$Checked','Pg407FailedRootRecovery','Pg410KnownAuthRecovery','Pg410KnownAuthRecovery$Receipt','Pg422KnownIncompleteRecovery','Pg422SignedMigration','Pg422SignedMigration$Data','Pg423AssetFixtureRecovery','Pg424KnownApiRecovery','Pg425KnownApiRecovery','Pg428ColdBootPreparation','Pg428ColdBootPreparation$1Node','Pg456SignedMigration','Pg456SignedMigration$Data']
files={n+'.class':work/'pg456-tools-v3'/(n+'.class') for n in names}
files.update({'release.tar':private/'pg456-release.tar','manifest.sig':private/'pg456-manifest.sig','watch.py':work/'pg456_watch_parent.py'})
expected={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()}
assert expected['release.tar']=='02c9de7c2c5d9ba0bd561e55e3463e8ae8714f9d93a167de87e39c0ade7feefe'
assert expected['manifest.sig']=='52d0e25e9ee16f8a51346d80337dc994277f38d22832a2c7e30c72d2dcc2a1d2'
assert expected['watch.py']=='6c18d8bb3309e7ea5d3a750c3fb32b4ecc91dc4dc812742d96d1eab77cc5daee'
subprocess.run(ssh+['umask 077; test ! -e /home/ubuntu/pg456-stage && mkdir /home/ubuntu/pg456-stage'],check=True)
for name,path in files.items():subprocess.run(scp+[str(path),'ubuntu@127.0.0.1:/home/ubuntu/pg456-stage/'+name],check=True)
payload='''import hashlib,grp,os,pathlib,stat,tarfile
assert os.geteuid()==0 and pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01'
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
incoming=pathlib.Path('/home/ubuntu/pg456-stage'); base=pathlib.Path('/var/lib/pgpt-s1-preservation'); release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG456')
tools=base/'pg456-deploy-tools'; sig=base/'pg456-manifest.sig'; watch=base/'pg456-watch.py'
for p in (release,tools,sig,watch):assert not p.exists() and not p.is_symlink()
assert set(p.name for p in incoming.iterdir())==set(EXPECTED)
for n,d in EXPECTED.items():
    p=incoming/n;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
    assert hashlib.sha256(p.read_bytes()).hexdigest()==d
group=grp.getgrnam('schubert').gr_gid
with tarfile.open(incoming/'release.tar','r:') as archive:
    members=archive.getmembers()
    for member in members:
        path=pathlib.PurePosixPath(member.name)
        assert not path.is_absolute() and '..' not in path.parts and (member.isfile() or member.isdir())
    release.mkdir(mode=0o750);os.chown(release,0,group)
    archive.extractall(release,filter='data')
def payload_mode(relative,is_directory):
    if is_directory:return 0o750
    return 0o750 if relative in ('operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector') else 0o640
for p in [release,*release.rglob('*')]:
    assert not p.is_symlink();s=p.lstat();assert stat.S_ISDIR(s.st_mode) or (stat.S_ISREG(s.st_mode) and s.st_nlink==1)
    os.chown(p,0,group);os.chmod(p,payload_mode(p.relative_to(release).as_posix(),p.is_dir()))
tools.mkdir(mode=0o700)
for n in sorted(EXPECTED):
    if not n.endswith('.class'):continue
    fd=os.open(tools/n,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
    with os.fdopen(fd,'wb') as stream:stream.write((incoming/n).read_bytes());stream.flush();os.fsync(stream.fileno())
    assert hashlib.sha256((tools/n).read_bytes()).hexdigest()==EXPECTED[n]
os.chmod(tools,0o500)
for target,name in [(sig,'manifest.sig'),(watch,'watch.py')]:
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
    with os.fdopen(fd,'wb') as stream:stream.write((incoming/name).read_bytes());stream.flush();os.fsync(stream.fileno())
    assert hashlib.sha256(target.read_bytes()).hexdigest()==EXPECTED[name]
assert hashlib.sha256((release/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='21affa1850d60f3a7d54f5dbcc37e12c6460563865771fa49a52a433fe91b424'
for p in [tools,base,release,release.parent]:
    fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG456_STAGE candidate=true rootClosedOperatorClasses=15 hashMatches=true priorUnchanged=true activation=false migration=false start=false permit=false')
'''
r=subprocess.run(ssh+['sudo -n /usr/bin/python3 -'],input=('EXPECTED='+repr(expected)+'\n'+payload).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print(r.stdout.decode(),end='')
if r.returncode:print('PG456_STAGE_REFUSED diagnosticsRedacted=true actual='+str(r.returncode))
raise SystemExit(r.returncode)
