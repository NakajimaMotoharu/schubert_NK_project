# PG352 sanitized selected PT

Date: 2026-09-28 JST. Source commit: `84763f857977508c9965ece2bb98ed28f1a146c1`. Host Java25.0.4/Maven3.9.12. No real `systemctl start` was issued.

| Test ID | Independent expected | Observed |
|---|---|---|
| BSTART001 | fixed Backup argv and root/policy/client/reap order, all owner close | PASS |
| BSTART002 | pre-start policy/root/interrupt fail before launch | PASS |
| BSTART003 | nonzero client exit is non-success | PASS |
| BSTART004 | timeout remains UNKNOWN/live then same-handle reap | PASS |
| BSTART005 | start exception/null handle/stream faults never upgrade UNKNOWN | PASS |
| BSTART006 | interrupt and post-start root drift retain UNKNOWN/owner | PASS |
| BSTART007 | factory null/wrong actor; harmless native `/usr/bin/true` only | PASS |
| BSTART008 | terminal client status monotonic; no Unit/worker receipt | PASS |

JUnit8/1suite failures0/errors0/skipped0; Batch SpotBugs0. New Production outer B/L/M/C missed0/0/0/0; nested Attempt0/0/0/0 and Status L/M/C0/0/0. Batch overall misses remain B15/L235/M92/C12 and are not accepted. This is a client-only provisional result, not parent continuity, actual Backup worker, release, or CHR acceptance.
