"""New-only isolated VM Inspector account/env/password provisioning; never prints secrets.

SS343 SSC119. Does not start a Unit, change release/approval/permit, or mutate business rows.
Existing artifacts are never replaced; a partial run remains a visible preservation checkpoint.
"""
import contextlib
import fcntl
import grp
import os
import pathlib
import pwd
import secrets
import stat
import subprocess

assert os.geteuid() == 0
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip() == 'pgpt-r2-20260927-01'
os.umask(0o077)

def sql(query):
    result = subprocess.run(['runuser', '-u', 'postgres', '--', 'psql', '-X', '-A', '-t',
                             '-v', 'ON_ERROR_STOP=1', '-d', 'schubert_nk'],
                            input=query, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    assert result.returncode == 0, 'fixed provisioning SQL unavailable'
    return result.stdout.strip()

def new_file(path, content, group, mode):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    try:
        os.fchown(fd, 0, group)
        os.fchmod(fd, mode)
        with os.fdopen(os.dup(fd), 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(fd)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)

with contextlib.ExitStack() as owners:
    for name in ('maintenance.lock', 'startup-admission.lock'):
        path = pathlib.Path('/run/schubert-nk') / name
        fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW)
        owners.callback(os.close, fd)
        held = os.fstat(fd)
        assert stat.S_ISREG(held.st_mode) and held.st_uid == held.st_gid == 0
        assert stat.S_IMODE(held.st_mode) == 0o600 and held.st_nlink == 1
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert (held.st_dev, held.st_ino) == (path.stat(follow_symlinks=False).st_dev,
                                              path.stat(follow_symlinks=False).st_ino)
    current = pathlib.Path('/run/schubert-nk/startup/epoch.current')
    assert not current.is_symlink() and current.read_text().startswith('NKEPOCH1\nstate=INVALID\n')
    units = ['schubert-nk-morning-controller.service', 'schubert-nk-backup.service',
             'schubert-nk-cleanup.service', 'schubert-nk-inbox-inspector.service',
             'schubert-nk-expiry-cleanup.service', 'artemis.service',
             'schubert-nk-api.service', 'schubert-nk-web.service', 'caddy.service']
    for unit in units:
        observed = subprocess.check_output(['systemctl', '--system', '--no-pager', 'show', unit,
                                            '--property=ActiveState,SubState,MainPID,ControlPID'], text=True)
        fields = dict(line.split('=', 1) for line in observed.strip().splitlines())
        assert fields['ActiveState'] in ('inactive', 'failed')
        assert fields['MainPID'] == fields['ControlPID'] == '0'
    account = 'schubert-inbox-inspector'
    try:
        pwd.getpwnam(account)
    except KeyError:
        pass
    else:
        raise AssertionError('existing Inspector account must not be replaced')
    try:
        grp.getgrnam(account)
    except KeyError:
        pass
    else:
        raise AssertionError('existing Inspector group must not be replaced')
    credential = pathlib.Path('/etc/schubert-nk/credentials/db-inbox-inspector')
    environment = pathlib.Path('/etc/schubert-nk/inbox-inspector.env')
    assert not credential.exists() and not credential.is_symlink()
    assert not environment.exists() and not environment.is_symlink()
    assert sql("select rolcanlogin and not rolsuper and not rolcreatedb and not rolcreaterole "
               "and rolpassword is null from pg_authid where rolname='schubert_inbox_inspector';") == 't'
    subprocess.run(['groupadd', '--system', account], check=True)
    subprocess.run(['useradd', '--system', '--gid', account, '--groups', 'schubert,schubert-read',
                    '--home-dir', '/nonexistent', '--shell', '/usr/sbin/nologin', account], check=True)
    identity = pwd.getpwnam(account)
    assert identity.pw_uid > 0 and identity.pw_gid == grp.getgrnam(account).gr_gid
    actual_groups = set(os.getgrouplist(account, identity.pw_gid))
    expected_groups = {identity.pw_gid, grp.getgrnam('schubert').gr_gid, grp.getgrnam('schubert-read').gr_gid}
    assert actual_groups == expected_groups
    password = secrets.token_hex(32)
    # O_EXCL/Root0600 publication before SQL: uncertain SQL leaves a private visible fixture,
    # never regenerates/overwrites it or changes an already-set database password.
    new_file(credential, (password + '\n').encode('ascii'), 0, 0o600)
    sql("alter role schubert_inbox_inspector password '" + password + "';")
    password = None
    new_file(environment,
             b'NK_INSPECTOR_DB_URL=jdbc:postgresql://127.0.0.1:5432/schubert_nk\n'
             b'NK_INSPECTOR_FINGERPRINT_VERSIONS=v1\n', grp.getgrnam('schubert').gr_gid, 0o640)
    assert credential.stat().st_uid == credential.stat().st_gid == 0
    assert stat.S_IMODE(credential.stat().st_mode) == 0o600
    assert sql("select rolpassword is not null from pg_authid where rolname='schubert_inbox_inspector';") == 't'
    print('PG389 INSPECTOR_PROVISIONED fixedRole=true dedicatedOS=true explicitGroups=true '
          'credentialRoot0600=true environmentRootSchubert0640=true unitsStarted=0 permitsIssued=0')
