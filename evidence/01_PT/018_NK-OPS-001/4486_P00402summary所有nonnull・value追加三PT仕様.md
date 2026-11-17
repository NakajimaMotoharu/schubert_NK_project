# P00402 summary通常所有と三value契約

SS332/331/341・RD OPS009/DAT009/UI251、PG-D1173/BUG3174/YKT2643。元summary whole11（Port9/BatchBoundary2）と現helper8のsource/oracleを保持し、新3を加えた必要whole22を当sourceで一回実測する。旧helperとrepo CPタグ差がある原11を再演/成功転用しない。

PGは既借用Connectionを取得/閉鎖/commit/rollback/設定変更せず、null statement/rowは所有try開始前に既presentの固定SQLDataExceptionへ拒否、非nullの取得物だけをexactly-once close。元SQL/timeout5/UUIDとUTC cutoff/bind順/空rowとzero counts/close前後interrupt/固定catalog/現在のSQL graph fatal方針を維持する。Main所有は当repo一sourceに限定、actual DB/Root/cohort/VM/key/heldAPI型へ拡大しない。

新PT-SUM-RAW001 InspectionSummaryの全component/同値別instance/identity/null/型違い/complete差・redacted表示とhash、002 BatchRunの二field/固定hash/非漏洩表示、003 CleanupCounts三field/全getter/固定toString/hash/独立値差。hash vectorはUUID(0,1)・Instant epoch1793836800+nano123456000からJDK31進/Boolean値を独立計算、Instant=-499841792、BatchRun=-499841761、Counts(3,2,1)=2946、Summary(false)=688497394。期待値をproduction methodで生成しない。旧全正常/境界/異常/null/例外/並行fixtureは元19sourceに従う。追加.3/.8/2 cap3をP00402へ一回だけ、shared費を重複計上しない。
