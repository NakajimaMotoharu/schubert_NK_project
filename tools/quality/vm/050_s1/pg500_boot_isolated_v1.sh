#!/bin/bash
# PG500 / WBS-N11 / SS343 SSC165/174: saved guest, management-only cold boot.
# No old /run state restoration, business start, migration, or success inference.
set -euo pipefail
umask 077
exec 9>/home/mini/codex/project1/work/pgpt-vm/private/pg500-boot-guard.lock
flock -n 9
test -z "$(ps -eo comm= | rg '^qemu-system' || true)"
test -z "$(ss -H -lnt '( sport = :22222 )')"
test -z "$(lsof -t /home/mini/codex/project1/work/pgpt-vm/instance.qcow2 || true)"
test ! -e /home/mini/codex/project1/work/pgpt-vm/qemu-PG500-v1.pid
test ! -e /home/mini/codex/project1/work/pgpt-vm/console-PG500-v1.log
test ! -e /home/mini/codex/project1/work/pgpt-vm/qmp-PG500-v1.sock
export LD_LIBRARY_PATH=/home/mini/codex/project1/work/toolchain/qemu/root/usr/lib/x86_64-linux-gnu
/home/mini/codex/project1/work/toolchain/qemu/root/usr/bin/qemu-system-x86_64 \
  -name pgpt-r2 -machine q35,accel=kvm -cpu host -smp 4 -m 8192 \
  -L /home/mini/codex/project1/work/toolchain/qemu/root/usr/share/qemu \
  -bios /home/mini/codex/project1/work/toolchain/qemu/root/usr/share/seabios/bios-256k.bin \
  -kernel /home/mini/codex/project1/work/pgpt-vm/pg443-offline.eRv29R/vmlinuz \
  -initrd /home/mini/codex/project1/work/pgpt-vm/pg443-offline.eRv29R/initrd \
  -append 'root=UUID=92978eec-7925-481e-8629-5b963d59ced1 ro console=ttyS0 systemd.unit=basic.target systemd.wants=systemd-networkd.service systemd.wants=systemd-resolved.service systemd.wants=systemd-user-sessions.service systemd.wants=ssh.service systemd.wants=postgresql.service systemd.mask=timers.target systemd.mask=paths.target systemd.mask=snapd.socket systemd.mask=lxd-installer.socket' \
  -drive file=/home/mini/codex/project1/work/pgpt-vm/instance.qcow2,if=virtio,format=qcow2 \
  -drive file=/home/mini/codex/project1/work/pgpt-vm/seed.iso,media=cdrom,readonly=on \
  -netdev user,id=pgptnet,hostfwd=tcp:127.0.0.1:22222-:22 \
  -device virtio-net-pci,netdev=pgptnet,romfile= \
  -vga none -display none -monitor none \
  -qmp unix:/home/mini/codex/project1/work/pgpt-vm/qmp-PG500-v1.sock,server=on,wait=off \
  -serial file:/home/mini/codex/project1/work/pgpt-vm/console-PG500-v1.log \
  -pidfile /home/mini/codex/project1/work/pgpt-vm/qemu-PG500-v1.pid -daemonize
printf 'PG500 management-only isolated boot issued once; businessAcceptance=false\n'
