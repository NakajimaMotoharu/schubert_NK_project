# NK-OPS-001 外部Morning同一budget受渡し PT仕様（PG368）

対象`MorningProcessMain.main/run/Admission.verify`、`MorningParentBudget`。RD OPS-009/BAK-001、UI251、SS341 §5–6/342 §4/343、SSC107/BUG322/YKT254、471 R1/D04/D05。前段の同PID root Launcherとは別の、Morning Java外部entryで親単調30分budgetを一回生成し、保持Admission callbackへ同instanceを渡す。現行のread-only/固定exit30は変更しない。実Backup/Cleanup/Artemisやhard-timeoutを成功扱いしない。

| Test ID | 目的・fixture/input | 独立期待値 |
|---|---|---|
| PT-OPS-MMAIN006 | 引数0、合成Admissionが受領したbudgetを観測、`requireWithin()`実行 | callback1回、非null/親型の同instance、結果30。SS341の親一回生成と既存未結線exit30から算出 |
| PT-OPS-MMAIN007 | 不正argv、null、既知IO/stop、未知例外 | argv不正はAdmission0/70、nullは境界NPE、既知失敗30、未知は同一例外伝播。budgetを別stepで自動再発行しない |

既存MMAIN001～005の回帰とMBUDGET001～002/BUCYCLE006を同時実行。JDK25.0.4/Maven3.9.12、`./mvnw -o -q -Dmaven.repo.local=<fixed> -Dnk.pt.repository=<tree> -pl src/schubert-nk-batch -Dtest=MorningProcessMainTest,MorningParentBudgetTest,MorningBackupUnitCycleTest test spotbugs:check jacoco:report`。対象source commit、JUnit/coverage/実行日時/hashを次番号の結果に記載。期限30分を実時間待つ試験はここで代用せず、MBUDGET固定時計/外側systemd受入で検証する。RED・failed/skippedは合格算入しない。credential/token/原本は使わない。
