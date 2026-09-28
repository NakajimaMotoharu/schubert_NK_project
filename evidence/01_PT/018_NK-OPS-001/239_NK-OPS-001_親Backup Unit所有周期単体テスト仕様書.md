# 親Backup Unit所有周期 PT仕様（PG363、着手前）

Program NK-OPS-001、予定class `MorningBackupUnitCycle.execute`。RD OPS-009/BAK-001/BKO-001、UI251/253、SS341§5-6/343§6.15、SSC092/093/105/106、471 R1/D04/D05。`MorningBackupStage`の同一M/A/原本/DB/request callback内だけで使用する親側最小周期であり、callback単体はM/Aを取得しない。実worker archive・Cleanup・permitは本試験の合格範囲外。

| Test ID | 独立入力・操作 | 独立期待 |
|---|---|---|
| PT-OPS-BUCYCLE-001 | receiptのpre-start snapshot→固定Backup start client exit0→fresh Invocation/receipt0→明示stop client exit0→fresh全Unit終端→同原本/request確認 | この順以外でmarker retireせず、1回だけretire/結果を返す。SS341§5の順序から手書き期待 |
| PT-OPS-BUCYCLE-002 | start UNKNOWN/handleなし、receipt未成立、stop UNKNOWNを個別注入 | UNKNOWNで次段へ進まず、保持portへ入り、marker retire0。interruptも正常終了へ変えない |
| PT-OPS-BUCYCLE-003 | receipt/termination/root/原本確認のIOException・既知StopGateException | start後の不確実性を通常return/IOException unwindへ変えず、保持portへ入りready/retire0。start前baseline失敗はstart0 |
| PT-OPS-BUCYCLE-004 | client nonzero、post-stop終端不足、retire不明、null port/結果、二重retire | nonzeroをworker成功へ使わず、失敗時marker保全。null契約を正常化しない。固定失敗診断のみ |

Fixtureは固定Unit名・合成Process/receipt/終端port。成功時の期待event列はProduction methodから算出しない。`BackupUnitReceiptGate`実factoryのSS独立18field receipt0/真正kernel終端は既存BSTART/BGATE/BTERM PTを依存根拠とし、PG363は親順序と未確定保持を確認する。試験command、日時、commit、対象class coverage、全6影響範囲、raw XML hash、sanitized manifest/BUG・SSCを240へ記録する。BUG-322/SSC-107で判明した`Type=simple`の30分期限・子との起動順不整合が解消するまで外部親に本周期を結線しない。実VM起動/30分hard-timeout/恒久隔離は未達なら合格へ含めない。秘密/Invocation実値/Unit raw出力をGitへ格納しない。
