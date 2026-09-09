# NK-DAT-001 Inbox永続検査service単体テスト仕様書

RD DAT-009/MQ-008/OPS-009、UI212/241/251、SS324 §12.6/331 §3.8/341 §7.3/343、QA-046/UIC-006/SSC-049、BUG-014/YKT-012、PG-D-128。InboxCleanup.inspectStoredNext/runChunk、InspectionProgress、InboxInspectionProgressTest。旧PT033～040/057～064を同resource境界の回帰とする。

| Test ID | method / 条件・操作 | 独立期待 |
|---|---|---|
| PT-DB-INBOX-081 | mixedRowsPersistExactProgress / auth/query/User/SCN・不正/未知candidate | literal累積count/cursor、正当行だけ消失、保護行不変、ENDだけcomplete |
| PT-DB-INBOX-082 | boundedChunksResumeAndSkipCompleted / max1/1000、空run、複数instance/途中終了 | 部分false→保存cursorから再開、完了true→候補再走なし。run/cutoff固定 |
| PT-DB-INBOX-083 | progressAndBoundaryContracts / constructor・run/maxSteps・全nullable列・count/cursor不一致 | null/range fail-fast、DB不正は固定運用失敗、overflowしないfactory境界、内部ID非表示 |
| PT-DB-INBOX-084 | checkpointFaultsRollbackDeletion / open/recordのprepare/bind/query/result/close故障・空/重複 | DB初期化/削除/進捗は同rollback、障害を保護・END・成功にしない |
| PT-DB-INBOX-085 | uncertainCommitReloadsDurableCounts / commit前・commit後・connection close故障 | 前なら全復元、後なら行消失＋進捗増分の両方保存、同run再読で累積1だけ |
| PT-DB-INBOX-086 | ownsLocksWithoutSavepoints / delete直前/recordまでのbackup/参照/進捗lock、health | 外部NOWAIT55P03、途中commit0/SAVEPOINT0、成功commit/close各1、aborted TXは失敗 |
| PT-DB-INBOX-087 | concurrentAttemptsNeverDoubleCount / 100呼出し・33/33/34完了wave | 全future回収、一意削除/保護各1、累積2、END。予定競合は実観測55P03だけ |
| PT-DB-INBOX-088 | runIdentityKeysAndResultsStayPrivate / 別cutoff/run、unknown/closed key、read field不一致 | 誤run/cutoff拒否、検査不可は保護、結果/例外/logへcontext/token/key/wire値非出力 |

Fixtureは実PostgreSQL18.6・専用roleと独立UI TSV手組wire/JCE envelope。expectedはliteral値・SQL消失/残存/変更列で、production encoder/snapshot writer/集計を使わない。keysはtest実行時だけ生成・finally close、Gitへ格納しない。Jdbc probeはpublic interfaceへの故障注入だけでprivate実装reflection禁止。全null/例外/並行/再送は上記、全4種coverage100%/NullAway/SpotBugsは正式rootで確定する。

実行環境/command/対象commit/branch/時刻/exit/各Test ID・input・expected・actual/coverage/関連BUG/SSCとhashを024およびevidence/inbox-progress-service/manifestへ確定する。未実施、slice/Program/IT/ST完了には算入しない。
