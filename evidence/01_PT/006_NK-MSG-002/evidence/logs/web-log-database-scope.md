# PT-IDEM-20260906-02 Web log technical DB部分

対象commit `b13cd49784bf8994016a560760a8d49d4c7d6b32`、全reactor 242/242成功、failure/error/skipped0。
日時/command/環境/coverageは`PT-IDEM-20260906-02-run-summary.json`とmanifestへ固定。
PT-IDEM-012の部分実施であり、Web dispatcher/API ingest/HTTP response非置換は未実施。

- `encryptedInsertIsCallerAtomicDuplicateRetainsFirstAndWebCannotReachBusiness`: caller commit前・rollback後は別connectionから0、commit後1。同Message IDは更新0で最初のkey/ciphertext/identity/dueを保持。Web専用roleの業務app_logs読出しは42501。
- `dueAndStrictLeaseBoundariesSkipLocksLimit100AndNeverClaimSent`: due/未来、期限一致/失効、NULL lease、SENT、102件を実PostgreSQLで確認。2つの未commit transactionが100件/2件を重複0で取得、10秒lease、返却immutable。
- `resultUpdatesProtectOwnerAndPersistExactJitterAllStagesIncludingAttemptCap`: 7 attempt状態×3 jitter境界をDB後条件で確認。1/5/30/60/300秒baseの±10%/中点に一致し、100回以降もERROR/retryを継続。失敗時刻+delay、owner不一致/SENT更新0、成功でerror/lease clear。
- `nullInvalidDatabaseRowsAndBoundsFailClosedWithoutNpeRecovery`: API境界、DB全必須列のnull、layout/version、不正worker/limit/attempt/jitter/errorとN12境界。SQLDataException/constructor拒否であり、NPEをcatchして正常化していない。

暗号文64 byteの合成fixtureは保存・SQL後条件を確認するだけで、暗号認証/送信正常vectorではない。暗号codecの8試験とDB repository4試験は独立した責務として実行。
Production Webは業務schemaやAPI moduleへcompile依存せず、testだけが既導入Flyway13.4.0/pgJDBC42.7.13とproduction migration resourceを使う。
初回test fixtureのAutoCloseable/InterruptedException lint失敗はPASS算入外。明示的AfterAllのstopへ修正後に正式runを実施した。
