# PG353 sanitized selected PT

Date: 2026-09-28 JST. Source commit: `3578716cba2af02543c212f7174d3d2bc01e91ed`. Host Java25.0.4/Maven3.9.12. No real Unit start/stop or secret read.

| Test ID | SS-independent input/expected | Actual |
|---|---|---|
| BGATE001 | old/fresh fixed UUID and matching bus-kernel-bus sequence | PASS |
| BGATE002 | pre-start absent/mismatch/ABA/root drift cannot issue Baseline | PASS |
| BGATE003 | running/job, old Invocation, Backup status10 and failed receipt cannot pass | PASS |
| BGATE004 | kernel absence/mismatch and late bus replacement cannot pass | PASS |
| BGATE005 | null observer and foreign Gate token reject | PASS |
| BGATE006 | IOException, StopGateException, null after observation, interrupt/root drift reject | PASS |
| BGATE007 | MORNING-only factory, null/wrong actor; injected root recheck | PASS |
| BGATE008 | stale Invocation and late alternate fresh Invocation reject | PASS |

JUnit8/1suite F/E/S0, SpotBugs0. New outer B/L/M/C missed0/0/0/0 and Baseline L/M/C missed0/0/0. Batch overall missed B15/L235/M92/C12. First fixture construction attempt raised `List.of(null)` NPE and was excluded; later explicit mutable null-injection reached Production's fixed IOException boundary. This is one read-only observation step, not worker success or parent lifecycle acceptance.
