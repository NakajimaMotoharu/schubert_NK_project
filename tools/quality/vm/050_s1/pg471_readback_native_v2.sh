#!/bin/bash
# New read-only owned proof only after observer terminal normal0. Never start/stop/repair.
set -eu
umask 077
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
test ! -e "$task_work/pg471-readback-native-v2.private.log"
python3 -B - <<'PY'
import pathlib,json
w=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
rs=[json.loads(l) for l in (w/'pg471-parent-watch-private-v1.jsonl').read_text().splitlines() if l.strip()]
t=[r for r in rs if r.get('terminalObserved')];assert len(t)==1
r=t[0];assert r['parentResult']=='success' and r['parentCode'] in ['0','1'] and r['parentExit']=='0'
assert r['readyObserved']==r['rootsCaptured']==['api','web'] and r['caddyTlsLogin200'] and all(r['backendAlive'].values())
assert all(r['info']['commit']=='717d72dd844fff286b4c696b9d08c41b136f0a6c' for r in rs if r.get('ready'))
PY
task_cp='/var/lib/pgpt-s1-preservation/pg471-completed-tools-v2:/var/lib/pgpt-s1-preservation/pg469-current-tools-v3:/var/lib/pgpt-s1-preservation/pg471-readback-tools-v2:/var/lib/pgpt-s1-preservation/pg468-recovery-tools-v4:/var/lib/pgpt-s1-preservation/pg468-recovery-tools-v2:/var/lib/pgpt-s1-preservation/pg466-tool-v3:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v2:/var/lib/pgpt-s1-preservation/pg464-completed-readback-v7:/var/lib/pgpt-s1-preservation/pg464-code-tools-v2:/var/lib/pgpt-s1-preservation/pg461-known30-tool-v3:/var/lib/pgpt-s1-preservation/pg456-applied-tools-v7:/opt/schubert-nk/releases/0.1.0-PG471/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG471/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG471/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG471/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
task_exit=0
date --iso-8601=seconds > "$task_work/pg471-readback-native-v2.started"
ssh -i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts" ubuntu@127.0.0.1 "sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp '$task_cp' Pg471CompletedReadback" > "$task_work/pg471-readback-native-v2.private.log" 2>&1 || task_exit=$?
printf '%s\n' "$task_exit" > "$task_work/pg471-readback-native-v2.exit"
date --iso-8601=seconds > "$task_work/pg471-readback-native-v2.completed"
printf 'PG471_READBACK_NATIVE actualExit=%s readOnly=true starts0=true stops0=true\n' "$task_exit"
exit "$task_exit"
