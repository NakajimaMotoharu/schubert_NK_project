#!/usr/bin/env bash
set -euo pipefail
repo=/home/mini/codex/project1/work/pgpt-foundation
private=/home/mini/codex/project1/work/pgpt-vm/private
run=/home/mini/codex/project1/work/pgpt-runs/PG379
ssh_options=(-i "$private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$private/known_hosts")
scp_options=(-i "$private/vm-access" -P 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$private/known_hosts")
test ! -e "$run/pg410-native-start.log"
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'test ! -e /home/ubuntu/pg410-stage && mkdir -m700 /home/ubuntu/pg410-stage'
scp "${scp_options[@]}" "$run/pg393_readback_full.sql" "$repo/tools/quality/vm/050_s1/pg406_watch_root.py" "$repo/tools/quality/vm/050_s1/pg403_backup_inventory.py" ubuntu@127.0.0.1:/home/ubuntu/pg410-stage/
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n python3 -' > "$run/pg410-native-preconditions.log" 2>&1 <<'PY'
import pathlib, subprocess, hashlib
assert str(pathlib.Path('/opt/schubert-nk/current').readlink()) == '/opt/schubert-nk/releases/0.1.0-PG408'
for name in ('backup-request','cleanup-request','expiry-request','maintenance'):
    assert not list((pathlib.Path('/run/schubert-nk')/name).iterdir())
for unit in ('schubert-nk-morning-controller.service','schubert-nk-backup.service','schubert-nk-cleanup.service',
             'schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','artemis.service',
             'schubert-nk-api.service','schubert-nk-web.service'):
    raw = subprocess.check_output(['/usr/bin/systemctl','show',unit,'-p','MainPID','-p','ControlPID','-p','Job'],text=True)
    assert set(raw.splitlines()) == {'MainPID=0','ControlPID=0','Job='}
    tree = pathlib.Path('/sys/fs/cgroup/system.slice')/unit
    if tree.exists():
        assert not (tree/'cgroup.procs').read_text().strip()
        assert 'populated 0\n' in (tree/'cgroup.events').read_text()
startup = pathlib.Path('/run/schubert-nk/startup')
assert (startup/'epoch.current').read_bytes().startswith(b'NKEPOCH1\nstate=INVALID\n')
assert not (startup/'permit-start.intent').exists()
assert all(not p.name.endswith('.start.intent') for p in startup.iterdir())
# Test-only agent configuration is unchanged; saved PG406 bytes must match before overwrite.
old = pathlib.Path('/run/schubert-nk/pt-coverage/root-api/root-api.exec')
assert old.read_bytes() == b'' # PG408 actual same-PID exec left no shutdown-hook dump
print('PG410_PRECONDITIONS currentCandidate=true allKernelTerminal=true INVALID=true intentClear=true oldCorrelationArtifactsPreserved=true')
PY
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n -u postgres psql -X -v ON_ERROR_STOP=1 -d schubert_nk -f - < /home/ubuntu/pg410-stage/pg393_readback_full.sql' > "$run/pg410-native-db-before-full.log" 2>&1
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n python3 /home/ubuntu/pg410-stage/pg403_backup_inventory.py' > "$run/pg410-backup-before-private.json"
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n python3 /home/ubuntu/pg410-stage/pg406_watch_root.py' > "$run/pg410-root-watch-private.jsonl" 2>&1 &
watch_pid=$!
printf 'PG410 root watch host PID=%s\n' "$watch_pid"
ssh "${ssh_options[@]}" ubuntu@127.0.0.1 'sudo -n systemctl --no-block start schubert-nk-morning-controller.service' > "$run/pg410-native-start.log" 2>&1
printf 'PG410 external Morning delivered once: not readiness or worker success\n'
wait "$watch_pid"
