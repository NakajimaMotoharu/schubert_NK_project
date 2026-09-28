# 229 NK-OPS-001 Backup新規実行receipt PT仕様（PG353）

状態: 固定Backup Unit観測の限定PT。実Unit起動・親のM/A連続保持・archive現物・正式R2は未認定。

| 項目 | 契約 |
|---|---|
| Program/class/method | NK-OPS-001 `BackupUnitReceiptGate.capture/observe` と内部`Baseline` |
| 関連正本 | OPS-009、BAK-001、UI251、SS341§5/§6.1、SS343§6.15、SSC-092/093/105、BUG-308、BUG-315/YKT-248 |
| fixture | SS341の固定18fieldを独立literalで構築した`InspectorUnitSnapshot.Target.BACKUP`、injectしたread-only bus+kernel observer、MORNING actor fixture。実Unit変更なし |
| 期待値独立性 | 前後Invocation IDは固定UUID vector。`ExecMainCode=1`/`ExecMainStatus=0`/`Result=success`はSS341値、Unit前後18field一致、kernel全process空は別fixture。Productionのreceipt methodをexpected生成には使わない |

| Test ID | 入力・操作 | 期待値・異常/境界 |
|---|---|---|
| PT-OPS-BGATE001 | 起動前cold Unitとkernel終端が同一→Baseline取得、後に別fresh Invocation/receipt0/同kernel全終端を2回読取 | `observe`が同fresh snapshotのみ返す。順序root→probe→kernel→probe→root、後段も同順、旧Invocationをworker成功にしない |
| PT-OPS-BGATE002 | 起動前Unit/全process不在、bus-kernel/前後ABA不一致、root失効 | Baselineを渡さず拒否。callerが不明状態を成功へ移さない |
| PT-OPS-BGATE003 | 起動後running/job残存、旧Invocation、status10/非0、failed、欠落/未知field | `observe`はempty又は既知拒否。BackupはInspector status10を成功へしない |
| PT-OPS-BGATE004 | 起動後bus receipt0だがkernel whole Unit空なし、bus-kernel不一致、後段bus差替え | `observe` empty。managerの空応答だけでkernel終端を代用しない |
| PT-OPS-BGATE005 | null Baseline/他GateのBaseline、null observer/戻り値 | null契約又は固定IOException。古い別runのtokenを再利用不可 |
| PT-OPS-BGATE006 | observer IOException/StopGateException/interrupt | 不明を成功へ変換せず親へ失敗を伝え、M/Aをこのclassで解放しない |
| PT-OPS-BGATE007 | MORNING factory null/wrong service、固定Backup target | 他Unit/任意path選択不可。read-only観測以外のUnit操作0 |
| PT-OPS-BGATE008 | fresh receipt後の再観測ABA/二重判定 | baseline/固定UUIDとの一致以外の経路でsuccess0。値が不変の安定3点のみ採用 |

実行環境・command・source commit・4指標coverage・結果・BUG/SSC・sanitized evidence path/hashは[230](230_NK-OPS-001_Backup新規実行receipt_実行結果.md)に記録する。callerは連続M/A/同原本・固定requestと同一runを保持し、単調30分budget内でpollする。本Gate単独はpoll・起動・停止・backup DB更新をしない。観測失敗後のworker終端/UNKNOWN隔離は親の別必須gate。
