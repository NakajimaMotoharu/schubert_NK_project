#!/bin/bash
# WBS-N11 / SS343 SSC174: read-only offline guard and private disk preservation.
set -euo pipefail
umask 077
export LD_LIBRARY_PATH=/home/mini/codex/project1/work/toolchain/qemu/root/usr/lib/x86_64-linux-gnu
test -z "$(ps -eo comm= | rg '^qemu-system' || true)"
test -z "$(lsof -t /home/mini/codex/project1/work/pgpt-vm/instance.qcow2 || true)"
test ! -e /home/mini/codex/project1/work/pgpt-vm/private/pg500-offline-location
capture_dir=$(mktemp -d /home/mini/codex/project1/work/pgpt-vm/private/pg500-offline.XXXXXX)
source_disk=/home/mini/codex/project1/work/pgpt-vm/instance.qcow2
source_identity=$(stat -c '%d:%i:%s:%Y:%Z' "$source_disk")
cp --reflink=auto --sparse=always -- "$source_disk" "$capture_dir/checkpoint.qcow2"
test "$source_identity" = "$(stat -c '%d:%i:%s:%Y:%Z' "$source_disk")"
sha256sum "$source_disk" "$capture_dir/checkpoint.qcow2" > "$capture_dir/disk.sha256"
test "$(cut -d ' ' -f 1 "$capture_dir/disk.sha256" | uniq | wc -l)" = 1
/home/mini/codex/project1/work/toolchain/qemu/root/usr/bin/qemu-img convert \
  -f qcow2 -O raw -S 4096 "$capture_dir/checkpoint.qcow2" "$capture_dir/disk.raw"
/usr/sbin/sfdisk --json "$capture_dir/disk.raw" > "$capture_dir/partitions.json"
python3 -B - "$capture_dir/partitions.json" <<'PY'
import json,sys
table=json.load(open(sys.argv[1]))['partitiontable']
parts=table['partitions']
assert table['sectorsize']==512 and len(parts)==4
assert parts[0]['start']==2324480 and parts[0]['size']==81561567
PY
dd if="$capture_dir/disk.raw" of="$capture_dir/rootfs.raw" \
  iflag=skip_bytes,count_bytes skip=1190133760 count=41759522304 bs=4M conv=sparse status=none
for path in /etc/systemd/system/basic.target.wants /etc/systemd/system/multi-user.target.wants \
  /etc/systemd/system/schubert-nk-morning-controller.service.d /usr/lib/tmpfiles.d; do
  debugfs -R "ls -l $path" "$capture_dir/rootfs.raw" >> "$capture_dir/offline-unit-list.private.log" 2>&1
done
test "$source_identity" = "$(stat -c '%d:%i:%s:%Y:%Z' "$source_disk")"
test -z "$(lsof -t "$source_disk" || true)"
printf '%s\n' "$capture_dir" > /home/mini/codex/project1/work/pgpt-vm/private/pg500-offline-location
printf 'PG500_OFFLINE_CAPTURE privateDiskPreserved=true sourceUnchanged=true businessActions=0\n'
