# PG351 native isolated-root observations (sanitized)

Date: 2026-09-28 JST. Candidate SHA-256 `27ccf8ae530a1ca83c2a8b2e7aa391d739757b2768c2ac76312d7ef834776e95`. VM systemd 259.5-0ubuntu3.4. No live `/run` tmpfiles command was run.

Boot-only candidate applied to a newly-created VM alternate root with `systemd-tmpfiles --create --boot --root=<new root> <candidate>`: exit0. Its seven paths were root:root with these independent SS-expected modes: `/run/schubert-nk` d0755; `maintenance`, `startup`, `backup-request`, `cleanup-request` d0700; `maintenance.lock`, `startup-admission.lock` f0600. A second identical alternate-root application exited0 and all seven inode numbers were unchanged. Both lock files had size0/nlink1; the three newly-added directories had only basic ACL entries. No request payload or `.part` was created.

Without `--boot`, the same candidate applied to a different new alternate root exited0 and `/run/schubert-nk` did not exist. Real VM `/run` mount type was tmpfs; real `backup-request` directory was root:root0700 from PG350 manual provisioning and remained empty. Both observed Units were inactive. This is a configuration-level native PT, not an actual reboot, Unit startup, or completed backup.

An initial non-root Host alternate-root attempt exited73 on seven fchown operations and was excluded from PASS.
