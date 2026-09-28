# NK-OPS-001 残存marker拒否の対照実OS PT仕様（PG376）

PG374 `PT-OPS-MTIME005～007`の独立oracle補強。Production `BackupStartIntentFiles.requireClear/begin`は不変更、PGPT-only probeに空namespace対照`clear`を追加する。RD OPS-009/BAK-001、UI251、SS341§5–6/343§6.15、SSC107、BUG322/YKT254。

| Test ID | 入力・操作 | Production結果から生成しない独立期待 |
|---|---|---|
| PT-OPS-MTIME009 | PG374と同じ固定instance-id/専用root0700の空状態で`clear`→同rootでProduction marker `hold`をoneshot2秒timeout→別process`check`→そのtest-only markerだけのinode/属性を検査して削除後`clear`を再実行 | 空rootは両時点で`CLEAR_ACCEPTED`/exit0。中間のみ空root0600/link1/size0 marker残存と`RESIDUAL_REFUSED`/exit0、Unit Result=timeout/PID0。前後で元Morning Unit、Production backup-request/current/credential不変更。単なる環境恒常失敗を残存marker拒否と誤認しない |

ProbeをProduction JARへ入れず、同source classと固定VM classpathのhash/command/exit/OS/JDK、marker前後、cleanup、Coverage非認定を263/manifestへ保存。例外のraw cause・journal/Invocation/秘密はGit保存しない。実親M/A/原本/30分/子Unit・外部Web/API/CHRの受入には算入しない。失敗時はtest-only対象だけを安全確認して扱う。
