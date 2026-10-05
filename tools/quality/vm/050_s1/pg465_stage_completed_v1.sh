#!/bin/bash
# SSC190 new-only signed placement and immutable management tool. No current/permit/start.
# Historical PG465 first placement only (pre-BUG719); current acceptance uses
# completed tool host-v3/root-v2 and pg465_completed_native_v2.sh. Do not reuse
# this script to replace the already placed candidate or newer tool.
set -eu
umask 077
task_repo=/home/mini/codex/project1/work/pgpt-foundation
task_work=/home/mini/codex/project1/work/pgpt-runs/PG379
task_private=/home/mini/codex/project1/work/pgpt-vm/private
task_digest=8b8e82f43146f4a89e02237a0b28e010442c59d3e7c8066c96f13d8b414d8e9e
task_ssh=(-i "$task_private/vm-access" -p 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
task_scp=(-i "$task_private/vm-access" -P 22222 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=$task_private/known_hosts")
cd "$task_repo"
test ! -e "$task_private/pg465-release.tar"
test -f "$task_work/pg465-completed-tool-v2/Pg465CompletedDeployment.class"
test "$(sha256sum "$task_work/pg465-release-v2/RELEASE-MANIFEST.json" | cut -d' ' -f1)" = "$task_digest"
tar -C "$task_work/pg465-release-v2" -cf "$task_private/pg465-release.tar" .
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 'test ! -e /home/ubuntu/pg465-stage && mkdir -m 700 /home/ubuntu/pg465-stage && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg465-completed-tool-v1'
scp "${task_scp[@]}" "$task_private/pg465-release.tar" "$task_private/pg465-manifest.sig" tools/quality/vm/050_s1/place_followup.py tools/quality/vm/050_s1/pg465_live_peer_check.py tools/quality/vm/050_s1/pg457_stable_actor.py tools/quality/vm/050_s1/pg462_observer_identity.py "$task_work/pg465-completed-tool-v2/"*.class ubuntu@127.0.0.1:/home/ubuntu/pg465-stage/ > "$task_work/pg465-stage-copy-v1.log" 2>&1
ssh "${task_ssh[@]}" ubuntu@127.0.0.1 "sudo -n python3 /home/ubuntu/pg465-stage/place_followup.py PG465 $task_digest && sudo -n install -d -o root -g root -m 700 /var/lib/pgpt-s1-preservation/pg465-completed-tool-v1 && sudo -n cp /home/ubuntu/pg465-stage/*.class /home/ubuntu/pg465-stage/pg465_live_peer_check.py /home/ubuntu/pg465-stage/pg457_stable_actor.py /home/ubuntu/pg465-stage/pg462_observer_identity.py /var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/ && sudo -n chown -R root:root /var/lib/pgpt-s1-preservation/pg465-completed-tool-v1 && sudo -n find /var/lib/pgpt-s1-preservation/pg465-completed-tool-v1 -maxdepth 1 -type f -exec chmod 400 {} +" > "$task_work/pg465-stage-place-v1.log" 2>&1
printf 'PG465_PLACED signedCandidate=true currentUnchanged=true starts0=true permits0=true\n'
