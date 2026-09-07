# PT-IDEM-006 transaction/failpoint result

Run `PT-IDEM-20260905-01` used a rootless PostgreSQL 18.6 cluster and the production Flyway V001-V005 schema. All identifiers, keys and operation tokens were synthetic in-memory fixtures and are not recorded here.

| Controlled point | Transaction action | Independent DB after-condition | Result |
|---|---|---|---|
| Handler entered after PROCESSING INSERT | Insert bounded audit row, then throw SQLSTATE 40001; caller rollback | Inbox 0, audit 0 | PASS |
| Handler returned and Inbox terminal UPDATE completed | Caller rollback instead of commit | Inbox 0, audit 0 | PASS |
| Handler/audit/Inbox terminal UPDATE completed | Caller commit | Inbox 1, audit 1 | PASS |
| Commit completed, same Message ID redelivered | Invoke coordinator with handler counter | REPLAY, handler 0, Inbox/audit unchanged | PASS |
| Initial SELECT completed, competing Message ID committed before INSERT | Real PK SQLSTATE 23505; rollback to savepoint and reread once | One PROCESSING row, IN_PROGRESS | PASS |
| Initial SELECT completed, competing owner/token committed before INSERT | Real partial unique SQLSTATE 23505; rollback to savepoint and reread once | One PROCESSING row, IN_PROGRESS | PASS |
| PROCESSING row removed by controlled handler before terminal UPDATE | UPDATE row count 0 | STATE_CORRUPT, caller rollback | PASS |

The coordinator neither commits nor rolls back the caller's whole transaction. It only rolls back its own failed INSERT to a savepoint for SQLSTATE 23505 recovery. No XA path is used.
