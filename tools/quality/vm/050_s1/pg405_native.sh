#!/usr/bin/env bash
set -euo pipefail
private=/home/mini/codex/project1/work/pgpt-vm/private
run=/home/mini/codex/project1/work/pgpt-runs/PG379
ssh_options=(-i "$private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$private/known_hosts")
scp_options=(-i "$private/vm-access" -P 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$private/known_hosts")
test ! -e "$run/pg405-native-start.log"
scp "${scp_options[@]}" "$run/pg393_readback_full.sql" ubuntu@127.0.0.1:/home/ubuntu/pg405-stage/pg393_readback_full.sql
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n python3 -' > "$run/pg405-native-preconditions.log" 2>&1 <<'PY'
import pathlib,subprocess
assert str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG405'
for name in ('backup-request','cleanup-request','expiry-request','maintenance'):
    assert not list((pathlib.Path('/run/schubert-nk')/name).iterdir()),name
for unit in ('schubert-nk-morning-controller.service','schubert-nk-backup.service','schubert-nk-cleanup.service',
             'schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','artemis.service',
             'schubert-nk-api.service','schubert-nk-web.service'):
    values=subprocess.check_output(['/usr/bin/systemctl','show',unit,'-p','MainPID','-p','ControlPID','-p','Job'],text=True)
    assert set(values.splitlines())=={'MainPID=0','ControlPID=0','Job='},unit
    p=pathlib.Path('/sys/fs/cgroup/system.slice')/unit
    if p.exists():
        assert not (p/'cgroup.procs').read_text().strip()
        assert 'populated 0\n' in (p/'cgroup.events').read_text()
startup=pathlib.Path('/run/schubert-nk/startup')
assert (startup/'epoch.current').read_bytes().startswith(b'NKEPOCH1\nstate=INVALID\n')
assert not (startup/'broker-start.intent').exists()
assert not (startup/'permit-start.intent').exists()
assert not any(p.name.endswith('.permit') for p in startup.iterdir())
print('PG405 PRECONDITIONS releaseFixed=true allKernelTerminal=true namespacesEmpty=true INVALID=true permitsIssued=0')
PY
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n -u postgres psql -X -v ON_ERROR_STOP=1 -d schubert_nk -f - < /home/ubuntu/pg405-stage/pg393_readback_full.sql' > "$run/pg405-native-db-before-full.log" 2>&1
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n systemctl --no-block start schubert-nk-morning-controller.service' > "$run/pg405-native-start.log" 2>&1
printf 'PG405 external Morning delivered: not worker-success evidence\n'
